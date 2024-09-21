from dataclasses import dataclass, asdict

import tempfile
import flask
import cv2
import numpy as np
import db.schema
import utils.errors
from werkzeug.exceptions import HTTPException

from .hold import create_hold, HoldModel
from .image import segment_holds_from_image, get_perspective_image

@dataclass
class WallModel:
    id: str
    name: str
    height: int
    width: int
    image: str
    routes: list
    holds: list

    @classmethod
    def from_mongo(cls, mongo_data):
        return cls(
            id=str(mongo_data['_id']),
            name=mongo_data['name'],
            height=mongo_data['height'],
            width=mongo_data['width'],
            image=mongo_data['image'],
            routes=mongo_data['routes'],
            holds=mongo_data['holds'],
        )

    def asdict(self):
        return asdict(self)

def register_wall(name, image, wall_annotations):
    # first validate that the name is unique
    walls = get_walls()
    for wall in walls:
        if wall['name'] == name:
            raise utils.errors.ValidationError("Wall with given name already exists.")

    perspective_image = get_perspective_image(image, wall_annotations)

    # get holds from image
    hold_models = segment_holds_from_image(perspective_image, cv_image=True)

    # upload image the perspective image to s3
    _, im_buf_arr = cv2.imencode(".jpg", perspective_image)
    byte_im = im_buf_arr.tobytes()
    with tempfile.NamedTemporaryFile(delete=False) as temp_image_file:
        temp_image_file.write(byte_im)
        temp_image_file.flush()  # Ensure all data is written to the file
        temp_image_file.seek(0)  # Go back to the start of the file
        uid = flask.current_app.extensions['s3'].upload_file(temp_image_file)

    # create holds
    holds = [create_hold(hold_model) for hold_model in hold_models]

    wall = db.schema.Wall(
        name=name,
        height=perspective_image.shape[0],
        width=perspective_image.shape[1],
        image=uid,
        holds=holds,
        routes=[],
    )

    with flask.current_app.app_context():
        wall.save()
    wall_id = wall.id

    return wall_id

def add_hold_to_wall(id, x, y):
    wall_doc = db.schema.Wall.objects(id=id).first()
    if not wall_doc:
        raise ValueError("Wall with given ID does not exist.")

    raise NotImplementedError("Not implemented")

def get_walls():
    print('get walls')
    walls = db.schema.Wall.objects().only('name', 'height', 'width', 'image', 'routes')
    walls = [WallModel.from_mongo(wall.to_mongo()).asdict() for wall in walls]

    return walls

def get_wall(id):
    wall_model = db.schema.Wall.objects(id=id).first()
    if not wall_model:
        raise ValueError("Wall with given ID does not exist.")
    
    # manually dereferencing because mongoengine won't apparently
    holds_data = [HoldModel.from_mongo(hold.to_mongo()) for hold in wall_model.holds]
    wall_model.holds = []
    
    wall_data = WallModel.from_mongo(wall_model.to_mongo()).asdict()
    wall_data['holds'] = holds_data
    wall_data['image'] = flask.current_app.extensions['s3'].get_file_url(wall_data['image'])

    return wall_data

def upload_new_image(id, new_wall_image):
    # Retrieve the old wall image from the database
    wall = db.schema.Wall.objects(id=id).first()
    if not wall:
        raise ValueError("Wall with given ID does not exist.")
    old_wall_image = wall.image

    # Get the affine transformation
    M = _get_affine_transform(old_wall_image, new_wall_image)

    # Segment the holds on the new wall image
    new_image, new_mask_image, new_holds = _segment_holds_from_image(new_wall_image)

    # Create a mapping of old holds to new holds based on proximity and matching threshold
    old_holds_mapped = {}
    for old_hold in wall.holds:
        old_hold_transformed_centroid = _apply_affine_transform_to_point(M, (old_hold.centroid_x, old_hold.centroid_y))
        # Calculate distances from the transformed centroid of the old hold to all new holds
        distances = [(hold, np.linalg.norm((hold.centroid_x - old_hold_transformed_centroid[0], hold.centroid_y - old_hold_transformed_centroid[1]))) for hold in new_holds]
        # Sort the distances and get the closest hold that is within the matching threshold
        closest_new_hold, closest_distance = min(distances, key=lambda x: x[1])
        if closest_distance < flask.current_app.config['SEGMENT_ANYTHING']['new_image_affine_match_threshold']:
            # Ensure that each new hold is only mapped to one old hold
            if closest_new_hold not in old_holds_mapped.values():
                old_holds_mapped[old_hold] = closest_new_hold

    # Determine which holds have been removed or added
    removed_holds = set(wall.holds) - set(old_holds_mapped.keys())
    added_holds = set(new_holds) - set(old_holds_mapped.values())

    # Update the holds that have remained
    for hold in wall.holds:
        if (hold.bbox, hold.centroid_x, hold.centroid_y) not in removed_holds:
            # Apply the affine transformation to the bbox and centroid
            hold.bbox = _apply_affine_transform_to_bbox(M, hold.bbox)
            hold.centroid_x, hold.centroid_y = _apply_affine_transform_to_point(M, (hold.centroid_x, hold.centroid_y))

    # Archive the old holds and add in the new holds
    for hold in removed_holds:
        hold.archive()  # Assuming there is a method to archive holds
    for hold in added_holds:
        wall.holds.append(hold)

    wall.image = new_image

    # Save the updated wall
    wall.save()

def _apply_affine_transform_to_bbox(M, bbox):
    # Transform the four corners of the bounding box
    points = np.array([
        [bbox[0], bbox[1]],
        [bbox[0], bbox[3]],
        [bbox[2], bbox[3]],
        [bbox[2], bbox[1]]
    ])
    # Apply the transformation to each point
    transformed_points = cv2.transform(np.array([points]), M)[0]
    # Find min and max points to get the transformed bbox
    min_x = min(point[0] for point in transformed_points)
    min_y = min(point[1] for point in transformed_points)
    max_x = max(point[0] for point in transformed_points)
    max_y = max(point[1] for point in transformed_points)
    # Return the transformed bbox as a list
    return [min_x, min_y, max_x, max_y]

def _apply_affine_transform_to_point(M, point):
    # Apply the affine transformation to the point
    transformed_point = cv2.transform(np.array([[point]]), M)[0][0]
    # Return the transformed point as a tuple
    return (transformed_point[0], transformed_point[1])

def _get_affine_transform(old_wall_image, new_wall_image):
    # Find keypoints and descriptors with SIFT
    sift = cv2.SIFT_create()
    keypoints_old, descriptors_old = sift.detectAndCompute(old_wall_image, None)
    keypoints_new, descriptors_new = sift.detectAndCompute(new_wall_image, None)

    # Match descriptors using FLANN matcher
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(descriptors_old, descriptors_new, k=2)

    # Store all the good matches as per Lowe's ratio test.
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    # Extract location of good matches
    points_old = np.float32([keypoints_old[m.queryIdx].pt for m in good_matches])
    points_new = np.float32([keypoints_new[m.trainIdx].pt for m in good_matches])

    # Find the affine transform
    M, mask = cv2.estimateAffinePartial2D(points_old, points_new)
    return M

