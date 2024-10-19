import io
import tempfile

import flask
import cv2
import numpy as np
import PIL.Image
import PIL.ImageDraw

import business.models.holds
import business.models.routes
import business.models.walls
import db.schema
import utils.errors

def register_wall(name: str, image: PIL.Image.Image, board_annotations: list):
    # first validate that the name is unique
    walls = get_walls()
    for wall in walls:
        if wall.name == name:
            raise utils.errors.ValidationError("Wall with given name already exists.")

    # remove the board background
    board_image = _remove_board_background(image, board_annotations)

    # upload the image to s3, get the url, and get the dimensions
    board_image_uid = _upload_image(board_image)
    board_image_url = flask.current_app.extensions['s3'].get_file_url(board_image_uid)

    # identify the holds
    hold_segments = flask.current_app.extensions['image_processing'].auto_segment(board_image_url)

    # create holds
    holds = [
        business.models.holds.create_hold_from_segment(hold_segment)
        for hold_segment in hold_segments
    ]

    # create the wall
    wall = db.schema.Wall(
        name=name,
        height=board_image.height,
        width=board_image.width,
        image=board_image_uid,
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

def delete_hold_from_wall(id, hold_id):
    wall_doc = db.schema.Wall.objects(id=id).first()
    if not wall_doc:
        raise ValueError("Wall with given ID does not exist.")

    hold = db.schema.Hold.objects(id=hold_id).first()
    if not hold:
        raise ValueError("Hold with given ID does not exist.")

def get_walls():
    walls = db.schema.Wall.objects().only('name', 'height', 'width', 'image', 'routes')
    walls = [business.models.walls.WallModel.from_mongo(wall) for wall in walls]

    return walls

def get_wall(id):
    wall_model = db.schema.Wall.objects(id=id).first()
    if not wall_model:
        raise ValueError("Wall with given ID does not exist.")
    
    # manually dereferencing because mongoengine won't apparently
    holds_data = [business.models.holds.HoldModel.from_mongo(hold) for hold in wall_model.holds]
    wall_model.holds = []
    
    wall_data = business.models.walls.WallModel.from_mongo(wall_model)
    wall_data.holds = holds_data
    wall_data.image = flask.current_app.extensions['s3'].get_file_url(wall_data.image)

    return wall_data

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
    climb_models = [
        business.models.routes.RouteModel.from_mongo(climb)
        for climb in climbs
    ]

    return climb_models

def _remove_board_background(image: PIL.Image.Image, board_annotations: list):
    """
    Remove the board background from an image using polygon annotations.

    Args:
        image (PIL.Image.Image): The image to remove the background from.
        board_annotations (list): List of (x, y) tuples representing the polygon vertices.

    Returns:
        PIL.Image.Image: The image with the background removed.
    """
    # Ensure image has an alpha channel
    image = image.convert("RGBA")

    # Create a mask for the polygon
    mask = PIL.Image.new('L', image.size, 0)
    polygon = [tuple(point) for point in board_annotations]
    PIL.ImageDraw.Draw(mask).polygon(polygon, outline=1, fill=1)

    # Convert the mask to an array
    mask_array = np.array(mask)

    # Apply the mask to the image
    image_array = np.array(image)
    image_array[..., 3] = mask_array * 255  # Set alpha channel based on mask
    # Set the background to white
    image_array[..., 0] = 255
    image_array[..., 1] = 255
    image_array[..., 2] = 255

    # Convert back to PIL Image
    result_image = PIL.Image.fromarray(image_array, 'RGBA')

    return result_image

def _upload_image(image: PIL.Image.Image):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_image_file:
        image.save(temp_image_file, format='PNG')
        temp_image_file.flush()  # Ensure all data is written to the file
        temp_image_file.seek(0)  # Go back to the start of the file
        uid = flask.current_app.extensions['s3'].upload_file(temp_image_file)

    return uid