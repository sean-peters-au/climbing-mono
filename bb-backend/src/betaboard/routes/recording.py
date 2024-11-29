import flask
import marshmallow

import betaboard.business.logic.recordings as recordings_logic
import betaboard.business.logic.recording_analysis.analysis as recording_analysis

recording_bp = flask.Blueprint('recording', __name__)


@recording_bp.route('/recording/start', methods=['POST'])
def start_recording() -> flask.Response:
    """
    Start recording a climbing attempt.

    Args:
        route_id (str): The ID of the route being climbed.

    Returns:
        Response: JSON response with the recording ID.
    """
    class StartRecordingSchema(marshmallow.Schema):
        route_id = marshmallow.fields.Str(required=True)

    try:
        StartRecordingSchema().load(flask.request.get_json())
    except marshmallow.exceptions.ValidationError as err:
        return flask.jsonify(err.messages), 400

    route_id = flask.request.get_json().get('route_id')
    
    try:
        recording_model = recordings_logic.start_recording(route_id)
        return flask.jsonify(recording_model.asdict()), 200
    except ValueError as e:
        return flask.jsonify({'error': str(e)}), 400


@recording_bp.route('/recording/<recording_id>/stop', methods=['POST'])
def stop_recording(recording_id: str) -> flask.Response:
    """
    Stop recording a climbing attempt.

    Args:
        recording_id (str): The ID of the recording to stop.

    Returns:
        Response: JSON response with the completed recording data.
    """
    try:
        recording_model = recordings_logic.stop_recording(recording_id)
        return flask.jsonify(recording_model.asdict()), 200
    except ValueError as e:
        return flask.jsonify({'error': str(e)}), 404


@recording_bp.route('/recording/<recording_id>/video', methods=['GET'])
def get_recording_video(recording_id: str) -> flask.Response:
    """
    Get the video URL for a recording.

    Args:
        recording_id (str): The ID of the recording to get the video URL for.

    Returns:
        Response: JSON response with the video URL.
    """
    video_url = recordings_logic.get_recording_video_url(recording_id)

    return flask.jsonify({'video_url': video_url}), 200

@recording_bp.route('/recording/analysis', methods=['POST'])
def analyze_recordings():
    """
    Analyze a list of recordings.

    Args:
        recording_ids (list[str]): The IDs of the recordings to analyze.

    Returns:
        Response: JSON response with the analysis results.
    """
    class AnalysisSchema(marshmallow.Schema):
        recording_ids = marshmallow.fields.List(marshmallow.fields.Str, required=True)

    try:
        AnalysisSchema().load(flask.request.get_json())
    except marshmallow.exceptions.ValidationError as err:
        return err.messages, 400

    recording_ids = flask.request.get_json().get('recording_ids')
    recordings = recordings_logic.get_recordings(recording_ids)

    analysis_results = recording_analysis.analyze_recordings(recordings)

    response = flask.jsonify({'analysis_results': analysis_results})

    return response, 200
