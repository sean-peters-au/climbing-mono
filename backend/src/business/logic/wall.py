import tempfile

import flask
import numpy as np
import PIL.Image
import PIL.ImageDraw

import business.models.holds
import business.models.routes
import business.models.walls
import db.dao.hold_dao
import db.dao.wall_dao
import db.schema

def register_wall(name: str, image: PIL.Image.Image, board_annotations: list):
    # Validate uniqueness of the wall name
    walls = db.dao.wall_dao.WallDAO.get_all_walls()
    if any(wall.name == name for wall in walls):
        raise ValueError("Wall with given name already exists.")

    # remove the board background
    board_image = _remove_board_background(image, board_annotations)

    # upload the image to s3, get the url, and get the dimensions
    board_image_uid = _upload_image(board_image)
    board_image_url = flask.current_app.extensions['s3'].get_file_url(board_image_uid)

    # identify the holds
    hold_segments = flask.current_app.extensions['image_processing'].auto_segment(board_image_url)

    # Create hold models
    hold_models = []
    for segment in hold_segments:
        hold_model = business.models.holds.HoldModel(
            bbox=segment.bbox,
            mask=segment.mask,
        )
        db.dao.hold_dao.HoldDAO.save_hold(hold_model)
        hold_models.append(hold_model)

    # Create wall model
    wall_model = business.models.walls.WallModel(
        name=name,
        height=board_image.height,
        width=board_image.width,
        image_id=str(board_image_uid),
        holds=hold_models,
    )
    db.dao.wall_dao.WallDAO.save_wall(wall_model)

    return wall_model.id

def add_hold_to_wall(id, x, y):
    wall_model = db.dao.wall_dao.WallDAO.get_wall_by_id(id)
    if not wall_model:
        raise ValueError("Wall with given ID does not exist.")

    image_url = flask.current_app.extensions['s3'].get_file_url(str(wall_model.image_id))

    # get the hold from the image processing service
    segment = flask.current_app.extensions['image_processing'].segment_hold(
        image=image_url,
        x=x,
        y=y,
    )

    # create the hold
    hold = business.models.holds.create_hold(segment)

    # add the hold to the wall
    wall_model.holds.append(hold)
    db.dao.wall_dao.WallDAO.save_wall(wall_model)

    return hold

def delete_hold_from_wall(id, hold_id):
    wall_model = db.dao.wall_dao.WallDAO.get_wall_by_id(id)
    if not wall_model:
        raise ValueError("Wall with given ID does not exist.")

    hold = db.dao.hold_dao.HoldDAO.get_hold_by_id(hold_id)
    if not hold:
        raise ValueError("Hold with given ID does not exist.")

def get_walls():
    walls = db.dao.wall_dao.WallDAO.get_all_walls()

    return walls

def get_wall(id):
    wall_model = db.dao.wall_dao.WallDAO.get_wall_by_id(id)
    wall_model.image_url = flask.current_app.extensions['s3'].get_file_url(wall_model.image_id)

    return wall_model

def add_route_to_wall(wall_id, name, description, grade, date, hold_ids):
    wall_model = db.dao.wall_dao.WallDAO.get_wall_by_id(wall_id)
    if not wall_model:
        raise ValueError("Wall with given ID does not exist.")

    # Fetch Hold objects
    holds = db.dao.hold_dao.HoldDAO.get_holds_by_ids(hold_ids)

    # Create a new climb (route)
    route = db.schema.Route(
        name=name,
        description=description,
        grade=grade,
        date=date,
        holds=holds,
        wall_id=wall_id,
    )
    route.save()

    # Add the route to the wall
    wall_model.routes.append(route)
    db.dao.wall_dao.WallDAO.save_wall(wall_model)

    return route

def get_routes_for_wall(wall_id):
    wall = db.schema.Wall.objects(id=wall_id).first()
    if not wall:
        raise ValueError("Wall with given ID does not exist.")

    # Fetch routes associated with the wall
    routes = db.schema.Route.objects(wall_id=wall)
    route_models = [
        business.models.routes.RouteModel.from_mongo(route)
        for route in routes
    ]

    return route_models

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