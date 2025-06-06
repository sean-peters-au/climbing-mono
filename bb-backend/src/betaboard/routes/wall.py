import base64
import http
import io

import flask
import marshmallow
import PIL

import betaboard.business.logic.wall as wall_logic
import betaboard.utils.encoding as encoding_utils

wall_bp = flask.Blueprint('wall', __name__)

@wall_bp.route('/wall', methods=['POST'])
def register_wall():
    class WallSchema(marshmallow.Schema):
        name = marshmallow.fields.Str(required=True)
        image = marshmallow.fields.Str(required=True)
        # [{x: 1, y: 1}, ...]
        wall_annotations = marshmallow.fields.List(marshmallow.fields.Tuple((marshmallow.fields.Int(), marshmallow.fields.Int())), required=True)

    try:
        WallSchema().load(flask.request.get_json())
    except marshmallow.exceptions.ValidationError as err:
        return err.messages, 400

    data = flask.request.get_json()
    name, image, wall_annotations = data.get('name'), data.get('image'), data.get('wall_annotations', [])

    # Decode the base64 encoded image and create a PIL image
    pil_image = PIL.Image.open(io.BytesIO(base64.b64decode(image)))
    wall_id = wall_logic.register_wall(name, pil_image, wall_annotations)

    return flask.jsonify({
        'id': str(wall_id)  # Convert ObjectId to string
    }), http.HTTPStatus.CREATED

@wall_bp.route('/wall', methods=['GET'])
def get_walls():
    walls = wall_logic.get_walls()

    return flask.jsonify({
        'walls': [wall_model.asdict() for wall_model in walls]
    }), http.HTTPStatus.OK

@wall_bp.route('/wall/<id>', methods=['GET'])
def get_wall(id):
    wall_model = wall_logic.get_wall(id)
    return flask.jsonify(wall_model.asdict()), http.HTTPStatus.OK

@wall_bp.route('/wall/<id>/hold', methods=['POST'])
def add_hold_to_wall(id):
    """
    Add a hold to a wall with a pre-supplied mask.

    Args:
        id (str): The ID of the wall.

    Returns:
        Response: JSON response with the added hold.
    """
    class HoldSchema(marshmallow.Schema):
        bbox = marshmallow.fields.List(
            marshmallow.fields.Int(),
            required=True,
            validate=marshmallow.validate.Length(equal=4)
        )
        mask = marshmallow.fields.List(
            marshmallow.fields.List(marshmallow.fields.Int()),
            required=True
        )

    try:
        data = HoldSchema().load(flask.request.get_json())
    except marshmallow.exceptions.ValidationError as err:
        return flask.jsonify(err.messages), http.HTTPStatus.BAD_REQUEST

    bbox = data['bbox']
    mask = data['mask']

    try:
        hold = wall_logic.add_hold_to_wall(id, bbox, mask)
    except ValueError as err:
        return flask.jsonify({'error': str(err)}), http.HTTPStatus.BAD_REQUEST

    return flask.jsonify(hold.asdict()), http.HTTPStatus.CREATED

@wall_bp.route('/wall/<id>/hold/<hold_id>', methods=['DELETE'])
def delete_hold_from_wall(id, hold_id):
    """
    Delete a hold from a wall.

    Args:
        id (str): The ID of the wall.
        hold_id (str): The ID of the hold to delete.

    Returns:
        Response: Empty response with HTTP 204 status.
    """
    try:
        wall_logic.delete_hold_from_wall(id, hold_id)
    except ValueError as err:
        return flask.jsonify({'error': str(err)}), http.HTTPStatus.NOT_FOUND

    return '', http.HTTPStatus.NO_CONTENT

@wall_bp.route('/wall/<id>/update_image', methods=['POST'])
def update_wall_image(id):
    """
    Updates the image for a wall.

    This will not only update the image, but also do many things such as:
    - Re-process the image for holds
    - Align old holds to new holds
    - Flag climbs that are now invalid
    """
    class UpdateWallImageSchema(marshmallow.Schema):
        image = marshmallow.fields.Str(required=True)

    try:
        data = UpdateWallImageSchema().load(flask.request.json)
    except marshmallow.exceptions.ValidationError as err:
        return flask.jsonify(err.messages), 400

    image = data['image']

    with encoding_utils.decode_base64_image(image) as image_file:
        wall_logic.upload_new_image(id, image_file)

    wall_model = wall_logic.get_wall(id)

    return flask.jsonify(wall_model.asdict()), http.HTTPStatus.OK

@wall_bp.route('/wall/<id>/route', methods=['POST'])
def add_route_to_wall(id):
    """
    Adds a climb to a wall.
    """
    class RouteSchema(marshmallow.Schema):
        name = marshmallow.fields.Str(required=True)
        description = marshmallow.fields.Str(required=False, default='')
        grade = marshmallow.fields.Int(required=True)
        date = marshmallow.fields.DateTime(format='iso', required=True)
        hold_ids = marshmallow.fields.List(marshmallow.fields.Str(), required=True)

    try:
        data = RouteSchema().load(flask.request.get_json())
    except marshmallow.exceptions.ValidationError as err:
        return flask.jsonify(err.messages), 400

    route = wall_logic.add_route_to_wall(
        id,
        data['name'],
        data['description'],
        data['grade'],
        data['date'],
        data['hold_ids']
    )

    return flask.jsonify({
        'route_id': str(route.id),
    }), http.HTTPStatus.CREATED

@wall_bp.route('/wall/<id>/route/<route_id>', methods=['PUT'])
def update_route_on_wall(id: str, route_id: str):
    """
    Update an existing route on a wall.

    Args:
        id (str): The ID of the wall.
        route_id (str): The ID of the route to update.

    Returns:
        Response: JSON response with the updated route.
    """
    class RouteUpdateSchema(marshmallow.Schema):
        name = marshmallow.fields.Str(required=False)
        description = marshmallow.fields.Str(required=False)
        grade = marshmallow.fields.Int(required=False)
        date = marshmallow.fields.DateTime(format='iso', required=False)
        hold_ids = marshmallow.fields.List(marshmallow.fields.Str(), required=False)

    try:
        data = RouteUpdateSchema().load(flask.request.get_json())
    except marshmallow.exceptions.ValidationError as err:
        return flask.jsonify(err.messages), http.HTTPStatus.BAD_REQUEST

    try:
        updated_route = wall_logic.update_route_on_wall(
            wall_id=id,
            route_id=route_id,
            update_data=data
        )
    except ValueError as err:
        return flask.jsonify({'error': str(err)}), http.HTTPStatus.NOT_FOUND

    return flask.jsonify(updated_route.asdict()), http.HTTPStatus.OK

@wall_bp.route('/wall/<id>/routes', methods=['GET'])
def get_routes_for_wall(id):
    try:
        routes = wall_logic.get_routes_for_wall(id)
    except ValueError as err:
        return flask.jsonify({'error': str(err)}), 404

    return flask.jsonify({'routes': [route.asdict() for route in routes]}), http.HTTPStatus.OK
