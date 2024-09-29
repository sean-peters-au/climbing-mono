import flask
import marshmallow

import business.logic.recordings

recordings_bp = flask.Blueprint('recordings', __name__)

@recordings_bp.route('/recording', methods=['POST'])
def create_recording():
    class RecordingSchema(marshmallow.Schema):
        start_time = marshmallow.fields.DateTime(required=True)
        end_time = marshmallow.fields.DateTime(required=True)
        route_id = marshmallow.fields.Str(required=True)

    try:
        RecordingSchema().load(flask.request.get_json())
    except marshmallow.exceptions.ValidationError as err:
        return err.messages, 400

    data = flask.request.get_json()
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    route_id = data.get('route_id')

    try:
        recording_model = business.recordings.create_recording(start_time, end_time, route_id)
        return flask.jsonify(recording_model.asdict()), 200
    except ValueError as e:
        return flask.jsonify({'error': str(e)}), 400

@recordings_bp.route('/recordings/<recording_id>/forces', methods=['GET'])
def get_recording_forces(recording_id):
    try:
        recording_model = business.logic.recordings.get_recording_forces(recording_id)
        return flask.jsonify(recording_model.asdict()), 200
    except ValueError as e:
        return flask.jsonify({'error': str(e)}), 404