import base64
import http
import flask
import business.wall
from marshmallow import Schema, fields, ValidationError
import tempfile
import os

wall_blueprint = flask.Blueprint('wall_blueprint', __name__)

@wall_blueprint.route('/wall', methods=['POST'])
def register_wall():
    class WallSchema(Schema):
        name = fields.Str(required=True)
        image = fields.Str(required=True)
        # [{x: 1, y: 1}, ...]
        wall_annotations = fields.List(fields.Tuple((fields.Int(), fields.Int())), required=True)

    try:
        WallSchema().load(flask.request.get_json())
    except ValidationError as err:
        return err.messages, 400

    data = flask.request.get_json()
    name, image, wall_annotations = data.get('name'), data.get('image'), data.get('wall_annotations', [])
    print(wall_annotations)

    # Decode the base64 encoded image and write to a temporary file
    with tempfile.NamedTemporaryFile(mode='wb+', delete=False) as temp_file:
        # image comes in base 64 encoded because who knows why some bugs occur
        # see another poor soul: https://stackoverflow.com/questions/76779195/sending-images-blob-data-to-a-server-with-multipart-form-data
        temp_file.write(base64.b64decode(image))
        temp_file.seek(0)  # Go to the beginning of the file to read it
        wall_id = business.wall.register_wall(name, temp_file, wall_annotations)
    os.unlink(temp_file.name)  # Clean up the temporary file

    return flask.jsonify({
        'id': str(wall_id)  # Convert ObjectId to string
    }), http.HTTPStatus.CREATED

@wall_blueprint.route('/wall', methods=['GET'])
def get_walls():
    walls = business.wall.get_walls()

    print(walls)
    return flask.jsonify({
        'walls': walls
    }), http.HTTPStatus.OK

@wall_blueprint.route('/wall/<id>', methods=['GET'])
def get_wall(id):
    wall = business.wall.get_wall(id)

    return flask.jsonify(wall), http.HTTPStatus.OK

@wall_blueprint.route('/wall/<id>/hold', methods=['POST'])
def add_hold_to_wall(id):
    class HoldSchema(Schema):
        x = fields.Int(required=True)
        y = fields.Int(required=True)

    try:
        data = HoldSchema().load(flask.request.json)
    except ValidationError as err:
        return flask.jsonify(err.messages), 400

    x = flask.request.json['x']
    y = flask.request.json['y']

    hold = business.wall.add_hold_to_wall(id, x, y)

    return flask.jsonify({
        'hold': hold,
    }), http.HTTPStatus.OK

@wall_blueprint.route('/wall/<id>/update_image', methods=['POST'])
def update_wall_image(id):
    if 'image' not in flask.request.files:
        return "No image provided", 400
    file = flask.request.files['image']
    if file.filename == '':
        return "No selected file", 400

    business.wall.upload_new_image(id, file)

    return flask.jsonify({}), http.HTTPStatus.OK

@wall_blueprint.route('/wall/<id>/climb', methods=['POST'])
def add_climb_to_wall(id):
    class ClimbSchema(Schema):
        name = fields.Str(required=True)
        description = fields.Str(required=False, allow_none=True)
        grade = fields.Int(required=True)
        date = fields.DateTime(format='iso', required=True)
        hold_ids = fields.List(fields.Str(), required=True)

    try:
        data = ClimbSchema().load(flask.request.get_json())
    except ValidationError as err:
        return flask.jsonify(err.messages), 400

    name = data['name']
    description = data.get('description', '')
    grade = data.get('grade', '')
    date_str = data.get('date', None)
    hold_ids = data['hold_ids']

    climb = business.wall.add_climb_to_wall(id, name, description, grade, date_str, hold_ids)

    return flask.jsonify({
        'climb_id': str(climb.id),
    }), http.HTTPStatus.CREATED

@wall_blueprint.route('/wall/<id>/climbs', methods=['GET'])
def get_climbs_for_wall(id):
    try:
        climbs = business.wall.get_climbs_for_wall(id)
    except ValueError as err:
        return flask.jsonify({'error': str(err)}), 404

    # Serialize the climbs
    climb_data = []
    for climb in climbs:
        print(climb)
        climb_dict = {
            'id': str(climb['id']),
            'name': climb['name'],
            'description': climb['description'],
            'grade': climb['grade'],
            'date': climb['date'],
            'hold_ids': [str(hold['id']) for hold in climb['holds']],
        }
        climb_data.append(climb_dict)

    return flask.jsonify({'climbs': climb_data}), http.HTTPStatus.OK