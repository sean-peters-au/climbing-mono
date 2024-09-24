import base64
import http
import os
import tempfile
import flask
import business.image
from marshmallow import Schema, fields, ValidationError

image_blueprint = flask.Blueprint('image_blueprint', __name__)

@image_blueprint.route('/image/auto_segment', methods=['POST'])
def image_auto_segment():
    # Marshmallow validation
    class ImageSchema(Schema):
        image = fields.Str(required=True)

    try:
        data = ImageSchema().load(flask.request.json)
    except ValidationError as err:
        return flask.jsonify(err.messages), 400

    image = flask.request.json['image']

    # Decode the base64 encoded image and write to a temporary file
    with tempfile.NamedTemporaryFile(mode='wb+', delete=False) as temp_file:
        temp_file.write(base64.b64decode(image))
        temp_file.seek(0)
        holds = business.image.segment_holds_from_image(image, temp_file)
    os.unlink(temp_file.name)

    return flask.jsonify({
        'holds': holds,
    }), http.HTTPStatus.OK

@image_blueprint.route('/image/segment_hold', methods=['POST'])
def image_segment_hold():
    class ImageCoordinateSchema(Schema):
        image = fields.Str(required=True)
        x = fields.Int(required=True)
        y = fields.Int(required=True)

    try:
        data = ImageCoordinateSchema().load(flask.request.json)
    except ValidationError as err:
        return flask.jsonify(err.messages), 400

    # Unimplemented
    return flask.jsonify({}, http.HTTPStatus.NOT_IMPLEMENTED)