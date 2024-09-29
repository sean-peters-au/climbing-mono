import http

import requests
import flask
import marshmallow

import business.logic.segmentation
import business.logic.transform
import utils.encoding

board_bp = flask.Blueprint('board_bp', __name__)

@board_bp.route('/board/auto_segment', methods=['POST'])
def board_auto_segment():
    """
    Segment climbing holds from an image of a climbing board.
    """
    class ImageSchema(marshmallow.Schema):
        image_url = marshmallow.fields.Url(required=True)

    try:
        data = ImageSchema().load(flask.request.json)
    except marshmallow.exceptions.ValidationError as err:
        return flask.jsonify(err.messages), 400

    image_url = data['image_url']
    image = requests.get(image_url).content
    holds = business.logic.segment.segment_holds_from_image(image, image_url)

    return flask.jsonify({
        'holds': holds,
    }), http.HTTPStatus.OK

@board_bp.route('/board/segment_hold', methods=['POST'])
def board_segment_hold():
    """
    Segment a hold from an image at a given coordinate.
    """
    class ImageCoordinateSchema(marshmallow.Schema):
        image_url = marshmallow.fields.Url(required=True)
        x = marshmallow.fields.Int(required=True)
        y = marshmallow.fields.Int(required=True)

    try:
        data = ImageCoordinateSchema().load(flask.request.json)
    except marshmallow.exceptions.ValidationError as err:
        return flask.jsonify(err.messages), 400

    image = requests.get(data['image_url']).content
    hold = business.logic.segmentation.segment_hold_from_image(
        image,
        data['x'],
        data['y'],
    )

    return flask.jsonify({
        'hold': hold,
    }), http.HTTPStatus.OK

@board_bp.route('/board/transform', methods=['POST'])
def board_transform():
    """
    Transform an image of a climbing board.
    """
    class KickboardSchema(marshmallow.Schema):
        annotations = marshmallow.fields.List(marshmallow.fields.Dict(required=True))

    class BoardSchema(marshmallow.Schema):
        annotations = marshmallow.fields.List(marshmallow.fields.Dict(required=True))

    class BoardTransformSchema(marshmallow.Schema):
        image = marshmallow.fields.Str(required=True)
        board = marshmallow.fields.Nested(BoardSchema, required=False)
        kickboard = marshmallow.fields.Nested(KickboardSchema, required=False)
        mask = marshmallow.fields.Bool(required=False)
        flatten = marshmallow.fields.Bool(required=False)

    try:
        data = BoardTransformSchema().load(flask.request.json)
    except marshmallow.exceptions.ValidationError as err:
        return flask.jsonify(err.messages), 400

    image = requests.get(data['image_url']).content
    transformed_image = business.logic.transform.transform_board(
        image=image,
        board=data['board'],
        kickboard=data['kickboard'],
        mask=data['mask'],
        flatten=data['flatten'],
    )

    upload_url = flask.current_app.extensions['s3'].upload_file(transformed_image)

    return flask.jsonify({
        'image_url': upload_url,
    }), http.HTTPStatus.OK
