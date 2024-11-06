import os
import subprocess

import flask
import flask_cors

import betaboard_camera.utils.config as config_utils


def create_app() -> flask.Flask:
    """
    Creates and configures the Flask application for the camera service.
    """
    app = flask.Flask(__name__)
    app.config.from_object(config_utils.Config)
    
    flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})

    @app.route('/video')
    def get_video():
        try:
            start_time = int(flask.request.args.get('start'))
            end_time = int(flask.request.args.get('end'))
        except (TypeError, ValueError):
            return flask.abort(400, 'Invalid or missing start/end parameters.')

        if start_time < 0 or end_time < 0 or start_time >= end_time:
            return flask.abort(400, 'Start time must be less than end time and non-negative.')

        segments_needed = []

        # Calculate which segments correspond to the requested time range
        for timestamp in range(start_time, end_time, app.config['VIDEO_SEGMENT_DURATION']):
            segment_index = ((timestamp // app.config['VIDEO_SEGMENT_DURATION']) % app.config['VIDEO_SEGMENT_NUMBER'])
            segment_filename = f'segment{segment_index:03d}.mp4'
            segment_path = os.path.join(app.config['VIDEO_DIR'], segment_filename)
            if os.path.exists(segment_path):
                segments_needed.append(segment_path)
            else:
                return flask.abort(404, f'Segment {segment_filename} not found.')

        # Create a file list for FFmpeg concatenation
        concat_file_path = '/tmp/concat.txt'
        with open(concat_file_path, 'w') as concat_file:
            for segment in segments_needed:
                concat_file.write(f"file '{segment}'\n")

        output_path = '/tmp/output.mp4'

        # Concatenate segments
        cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file_path,
            '-c', 'copy', output_path
        ]
        subprocess.run(cmd)

        return flask.send_file(output_path, mimetype='video/mp4')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000)