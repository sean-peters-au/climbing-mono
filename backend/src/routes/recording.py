import dateutil.parser

import flask
import marshmallow

import business.logic.recordings
import business.logic.recording_analysis.analysis

recording_bp = flask.Blueprint('recording', __name__)

@recording_bp.route('/recording', methods=['POST'])
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
    
    start_time = dateutil.parser.isoparse(data.get('start_time'))
    end_time = dateutil.parser.isoparse(data.get('end_time'))
    route_id = data.get('route_id')

    try:
        recording_model = business.logic.recordings.create_recording(start_time, end_time, route_id)
        return flask.jsonify(recording_model.asdict()), 200
    except ValueError as e:
        return flask.jsonify({'error': str(e)}), 400

@recording_bp.route('/recording/<recording_id>', methods=['GET'])
def get_recording(recording_id):
    try:
        recording_model = business.logic.recordings.get_recording(recording_id)
        return flask.jsonify(recording_model.asdict()), 200
    except ValueError as e:
        return flask.jsonify({'error': str(e)}), 404

@recording_bp.route('/recording/analysis', methods=['POST'])
def analyze_recordings():
    class AnalysisSchema(marshmallow.Schema):
        recording_ids = marshmallow.fields.List(marshmallow.fields.Str, required=True)

    try:
        AnalysisSchema().load(flask.request.get_json())
    except marshmallow.exceptions.ValidationError as err:
        return err.messages, 400

    recording_ids = flask.request.get_json().get('recording_ids')
    recordings = business.logic.recordings.get_recordings(recording_ids)

    analysis_results = business.logic.recording_analysis.analysis.analyze_recordings(recordings)

    response = flask.jsonify({'analysis_results': analysis_results})

    return response, 200
