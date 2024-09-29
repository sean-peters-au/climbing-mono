import tempfile
import flask
import cv2
import numpy as np

import business.models.holds
import business.models.routes
import business.models.walls
import db.schema
import utils.errors

def register_wall(name, image, wall_annotations):
    # first validate that the name is unique
    walls = get_walls()
    for wall in walls:
        if wall['name'] == name:
            raise utils.errors.ValidationError("Wall with given name already exists.")

    # transform the image
    transformed_image = flask.current_app.extensions['image_processing'].transform_board(
        image, board=wall_annotations, kickboard=True, mask=True, flatten=True
    )

    # identify the holds
    hold_models = flask.current_app.extensions['image_processing'].auto_segment(
        transformed_image, x=0, y=0,
    )

    # upload image the perspective image to s3
    _, im_buf_arr = cv2.imencode(".jpg", transformed_image)
    byte_im = im_buf_arr.tobytes()
    with tempfile.NamedTemporaryFile(delete=False) as temp_image_file:
        temp_image_file.write(byte_im)
        temp_image_file.flush()  # Ensure all data is written to the file
        temp_image_file.seek(0)  # Go back to the start of the file
        uid = flask.current_app.extensions['s3'].upload_file(temp_image_file)

    # create holds
    holds = [business.models.holds.create_hold(hold_model) for hold_model in hold_models]

    wall = db.schema.Wall(
        name=name,
        height=transformed_image.shape[0],
        width=transformed_image.shape[1],
        image=uid,
        holds=holds,
        routes=[],
    )

    with flask.current_app.app_context():
        wall.save()

    return wall.id

def add_hold_to_wall(id, x, y):
    wall_doc = db.schema.Wall.objects(id=id).first()
    if not wall_doc:
        raise ValueError("Wall with given ID does not exist.")

    image_url = flask.current_app.extensions['s3'].get_file_url(str(wall_doc.image))

    # get the hold from the image processing service
    segment = flask.current_app.extensions['image_processing'].segment_hold(
        image=image_url,
        x=x,
        y=y,
    )

    # create the hold
    hold = business.models.holds.create_hold(segment)

    # add the hold to the wall
    wall_doc.holds.append(hold)
    wall_doc.save()

    return hold

def get_walls():
    walls = db.schema.Wall.objects().only('name', 'height', 'width', 'image', 'routes')
    walls = [business.models.walls.WallModel.from_mongo(wall.to_mongo()).asdict() for wall in walls]

    return walls

def get_wall(id):
    wall_model = db.schema.Wall.objects(id=id).first()
    if not wall_model:
        raise ValueError("Wall with given ID does not exist.")
    
    # manually dereferencing because mongoengine won't apparently
    holds_data = [business.models.holds.HoldModel.from_mongo(hold.to_mongo().to_dict()) for hold in wall_model.holds]
    wall_model.holds = []
    
    wall_data = business.models.walls.WallModel.from_mongo(wall_model.to_mongo()).asdict()
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
    new_holds = flask.current_app.extensions['image_processing']._segment_holds_from_image(
        new_wall_image
    )

    # Create a mapping of old holds to new holds based on proximity and matching threshold
    old_holds_mapped = {}
    for old_hold in wall.holds:
        old_hold_transformed_centroid = _apply_affine_transform_to_point(M, (old_hold.centroid_x, old_hold.centroid_y))
        # Calculate distances from the transformed centroid of the old hold to all new holds
        distances = [
            (hold, np.linalg.norm(
                (hold.centroid_x - old_hold_transformed_centroid[0],
                 hold.centroid_y - old_hold_transformed_centroid[1])
            ))
            for hold in new_holds
        ]
        # Sort the distances and get the closest hold that is within the matching threshold
        closest_new_hold, closest_distance = min(distances, key=lambda x: x[1])
        if closest_distance < 5:
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

    wall.image = new_wall_image

    # Save the updated wall
    wall.save()

def add_climb_to_wall(wall_id, name, description, grade, date, hold_ids):
    wall = db.schema.Wall.objects(id=wall_id).first()
    if not wall:
        raise ValueError("Wall with given ID does not exist.")

    # Fetch Hold objects
    holds = db.schema.Hold.objects(id__in=hold_ids)

    # Create a new climb (route)
    climb = db.schema.Route(
        name=name,
        description=description,
        grade=grade,
        date=date,
        holds=holds,
        wall_id=wall,
    )
    climb.save()

    # Add the climb to the wall
    wall.routes.append(climb)
    wall.save()

    return climb

def get_climbs_for_wall(wall_id):
    wall = db.schema.Wall.objects(id=wall_id).first()
    if not wall:
        raise ValueError("Wall with given ID does not exist.")

    # Fetch climbs associated with the wall
    climbs = db.schema.Route.objects(wall_id=wall)
    climb_models = []
    for climb in climbs:
        climb_data = business.models.routes.RouteModel.from_mongo(climb.to_mongo()).asdict()
        # Populate holds with their details
        hold_details = [business.models.holds.HoldModel.from_mongo(hold.to_mongo()).asdict() for hold in climb.holds]
        climb_data['holds'] = hold_details
        climb_models.append(climb_data)

    return climb_models

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