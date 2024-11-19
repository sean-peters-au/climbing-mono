import datetime
import tempfile
import typing

import flask
import numpy as np
import PIL.Image
import PIL.ImageDraw

import betaboard.business.models.holds as holds_model
import betaboard.business.models.routes as routes_model
import betaboard.business.models.walls as walls_model
import betaboard.db.dao.hold_dao as hold_dao
import betaboard.db.dao.route_dao as route_dao
import betaboard.db.dao.wall_dao as wall_dao

def register_wall(name: str, image: PIL.Image.Image, board_annotations: list):
    # Validate uniqueness of the wall name
    walls = wall_dao.WallDAO.get_all_walls()
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
        hold_model = holds_model.HoldModel(
            bbox=segment.bbox,
            mask=segment.mask,
        )
        hold_dao.HoldDAO.save_hold(hold_model)
        hold_models.append(hold_model)

    # Create wall model
    wall_model = walls_model.WallModel(
        name=name,
        height=board_image.height,
        width=board_image.width,
        image_id=str(board_image_uid),
        holds=hold_models,
    )
    wall_dao.WallDAO.create_wall(wall_model)

    return wall_model.id

def add_hold_to_wall(
    wall_id: str,
    bbox: typing.List[int],
    mask: typing.List[typing.List[int]]
) -> holds_model.HoldModel:
    """
    Add a hold to a wall with a pre-supplied mask.

    Args:
        wall_id (str): The ID of the wall.
        bbox (List[int]): The bounding box of the hold [x_min, y_min, x_max, y_max].
        mask (List[List[int]]): The mask of the hold.

    Returns:
        HoldModel: The added hold model.
    """
    wall_model = wall_dao.WallDAO.get_wall_by_id(int(wall_id))
    if not wall_model:
        raise ValueError("Wall with the given ID does not exist.")

    # Create the hold model
    hold_model = holds_model.HoldModel(
        bbox=bbox,
        mask=mask
    )
    hold_dao.HoldDAO.save_hold(hold_model)

    # Add the hold to the wall
    wall_model.holds.append(hold_model)
    wall_dao.WallDAO.update_wall(wall_model)

    return hold_model

def delete_hold_from_wall(wall_id: str, hold_id: str) -> None:
    """
    Delete a hold from a wall.

    Args:
        wall_id (str): The ID of the wall.
        hold_id (str): The ID of the hold to delete.
    """
    wall_model = wall_dao.WallDAO.get_wall_by_id(int(wall_id))
    if not wall_model:
        raise ValueError("Wall with the given ID does not exist.")

    hold = next((h for h in wall_model.holds if h.id == hold_id), None)
    if not hold:
        raise ValueError("Hold with the given ID does not exist on the wall.")

    # Remove the hold from the wall
    wall_model.holds.remove(hold)
    wall_dao.WallDAO.update_wall(wall_model)

    # Delete the hold from the database
    hold_dao.HoldDAO.delete_hold(int(hold_id))

def get_walls():
    walls = wall_dao.WallDAO.get_all_walls()

    return walls

def get_wall(id):
    wall_model = wall_dao.WallDAO.get_wall_by_id(id)
    wall_model.image_url = flask.current_app.extensions['s3'].get_file_url(wall_model.image_id)

    return wall_model

def add_route_to_wall(
    wall_id: str,
    name: str,
    description: str,
    grade: int,
    date: datetime.datetime,
    hold_ids: typing.List[str]
) -> routes_model.RouteModel:
    wall_model = wall_dao.WallDAO.get_wall_by_id(int(wall_id))
    if not wall_model:
        raise ValueError("Wall with given ID does not exist.")

    holds = hold_dao.HoldDAO.get_holds_by_ids([int(hold_id) for hold_id in hold_ids])

    route = routes_model.RouteModel(
        name=name,
        description=description,
        grade=grade,
        date=date,
        wall_id=wall_id,
        holds=holds,
    )
    route_dao.RouteDAO.create_route(route)

    return route


def update_route_on_wall(
    wall_id: str,
    route_id: str,
    update_data: typing.Dict[str, typing.Any]
) -> routes_model.RouteModel:
    """
    Update an existing route on a wall.

    Args:
        wall_id (str): The ID of the wall.
        route_id (str): The ID of the route to update.
        update_data (Dict[str, Any]): The data to update on the route.

    Returns:
        RouteModel: The updated route model.
    """
    wall_model = wall_dao.WallDAO.get_wall_by_id(int(wall_id))
    if not wall_model:
        raise ValueError("Wall with the given ID does not exist.")

    route_model = route_dao.RouteDAO.get_route_by_id(int(route_id))
    if not route_model:
        raise ValueError("Route with the given ID does not exist.")

    if route_model.wall_id != wall_id:
        raise ValueError("Route does not belong to the specified wall.")

    # Update route fields
    route_model.name = update_data.get('name', route_model.name)
    route_model.description = update_data.get('description', route_model.description)
    route_model.grade = update_data.get('grade', route_model.grade)
    route_model.date = update_data.get('date', route_model.date)

    if 'hold_ids' in update_data:
        hold_ids = update_data['hold_ids']
        holds = hold_dao.HoldDAO.get_holds_by_ids([int(hid) for hid in hold_ids])
        route_model.holds = holds

    route_dao.RouteDAO.update_route(route_model)

    return route_model

def get_routes_for_wall(wall_id: str) -> typing.List[routes_model.RouteModel]:
    """Get all routes for a wall."""
    wall = wall_dao.WallDAO.get_wall_by_id(int(wall_id))
    if not wall:
        raise ValueError("Wall with given ID does not exist.")

    return wall.routes

def _remove_board_background(image: PIL.Image.Image, board_annotations: list):
    """
    Remove the board background from an image using polygon annotations.

    Args:
        image (PIL.Image.Image): The image to remove the background from.
        board_annotations (list): List of (x, y) tuples representing the polygon vertices.

    Returns:
        PIL.Image.Image: The image with the background removed.
    """
    # Ensure the image has an alpha channel
    image = image.convert("RGBA")

    # Create a mask for the polygon
    mask = PIL.Image.new('L', image.size, 0)
    polygon = [tuple(point) for point in board_annotations]
    PIL.ImageDraw.Draw(mask).polygon(polygon, outline=1, fill=1)

    # Convert the mask and image to NumPy arrays
    mask_array = np.array(mask)  # Values are 0 (outside polygon) or 1 (inside polygon)
    image_array = np.array(image)

    # Create a white background
    white_background = np.full(image_array.shape, fill_value=255, dtype=np.uint8)

    # Use the mask to blend the original image and the white background
    # Expand dimensions of the mask to match image array shape
    mask_3d = np.expand_dims(mask_array, axis=2)

    # Composite the images
    composite_array = image_array * mask_3d + white_background * (1 - mask_3d)

    # Ensure alpha channel is set correctly
    composite_array[..., 3] = mask_array * 255  # Set alpha channel based on mask

    # Convert back to PIL Image
    result_image = PIL.Image.fromarray(composite_array.astype('uint8'), 'RGBA')

    return result_image

def _upload_image(image: PIL.Image.Image):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_image_file:
        image.save(temp_image_file, format='PNG')
        temp_image_file.flush()  # Ensure all data is written to the file
        temp_image_file.seek(0)  # Go back to the start of the file
        uid = flask.current_app.extensions['s3'].upload_file(temp_image_file)

    return uid