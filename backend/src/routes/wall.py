import base64
import http
import io

import flask
import marshmallow
import PIL

import business.logic.wall
import utils.encoding

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
    wall_id = business.logic.wall.register_wall(name, pil_image, wall_annotations)

    return flask.jsonify({
        'id': str(wall_id)  # Convert ObjectId to string
    }), http.HTTPStatus.CREATED

@wall_bp.route('/wall', methods=['GET'])
def get_walls():
    walls = business.logic.wall.get_walls()

    return flask.jsonify({
        'walls': [wall.asdict() for wall in walls]
    }), http.HTTPStatus.OK

@wall_bp.route('/wall/<id>', methods=['GET'])
def get_wall(id):
    wall = business.logic.wall.get_wall(id)

    return flask.jsonify(wall.asdict()), http.HTTPStatus.OK

@wall_bp.route('/wall/<id>/hold', methods=['POST'])
def add_hold_to_wall(id):

    class HoldSchema(marshmallow.Schema):
        x = marshmallow.fields.Int(required=True)
        y = marshmallow.fields.Int(required=True)

    try:
        data = HoldSchema().load(flask.request.json)
    except marshmallow.exceptions.ValidationError as err:
        return flask.jsonify(err.messages), 400

    x = flask.request.json['x']
    y = flask.request.json['y']

    hold = business.logic.wall.add_hold_to_wall(id, x, y)

    return flask.jsonify({
        'hold': hold,
    }), http.HTTPStatus.OK

@wall_bp.route('/wall/<id>/hold', methods=['DELETE'])
def delete_hold_from_wall(id):
    class HoldSchema(marshmallow.Schema):
        hold_id = marshmallow.fields.Str(required=True)

    try:
        data = HoldSchema().load(flask.request.json)
    except marshmallow.exceptions.ValidationError as err:
        return flask.jsonify(err.messages), 400

    hold_id = data['hold_id']

    business.logic.wall.delete_hold_from_wall(id, hold_id)

    return flask.jsonify({}), http.HTTPStatus.NO_CONTENT

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

    with utils.encoding.decode_base64_image(image) as image_file:
        business.logic.wall.upload_new_image(id, image_file)

    wall = business.logic.wall.get_wall(id)

    return flask.jsonify(wall.asdict()), http.HTTPStatus.OK

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

    route = business.logic.wall.add_route_to_wall(
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

@wall_bp.route('/wall/<id>/routes', methods=['GET'])
def get_routes_for_wall(id):
    try:
        routes = business.logic.wall.get_routes_for_wall(id)
    except ValueError as err:
        return flask.jsonify({'error': str(err)}), 404

    return flask.jsonify({'routes': [route.asdict() for route in routes]}), http.HTTPStatus.OK
