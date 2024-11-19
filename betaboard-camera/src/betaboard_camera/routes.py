import traceback

import flask
import flask_cors

import betaboard_camera.logic
import typing


def init_app(app: flask.Flask) -> None:
    """
    Initialize routes and configurations on the Flask app.

    Args:
        app (flask.Flask): The Flask application instance.
    """
    flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})

    @app.route('/video')
    def get_video() -> flask.Response:
        """
        Handle the /video route to serve video segments.

        Returns:
            flask.Response: The response containing the video.
        """
        logger = app.logger

        try:
            start_time, end_time = _parse_request_parameters()
            output_data = betaboard_camera.logic.process_video_request(start_time, end_time)
            return flask.Response(
                output_data,
                mimetype='video/mp4',
                headers={'Content-Disposition': 'attachment; filename=output.mp4'}
            )
        except ValueError as e:
            logger.warning(f"ValueError: {e}")
            return flask.abort(404, str(e))
        except Exception as e:
            logger.error(f"Error processing video request: {e}")
            logger.error(traceback.format_exc())
            return flask.abort(500, 'Internal server error')

    @app.errorhandler(Exception)
    def handle_exception(e: Exception) -> flask.Response:
        """
        Handle uncaught exceptions and log them.

        Args:
            e (Exception): The exception that was raised.

        Returns:
            flask.Response: The response with an error message.
        """
        logger = flask.current_app.logger
        logger.error(f"Uncaught exception: {e}")
        logger.error(traceback.format_exc())
        return flask.abort(500, 'Internal server error')


def _parse_request_parameters() -> typing.Tuple[int, int]:
    """
    Parse and validate the start and end time parameters from the request.

    Returns:
        Tuple[int, int]: Validated start and end times as Unix timestamps.

    Raises:
        ValueError: If invalid or missing parameters are provided.
    """
    logger = flask.current_app.logger
    try:
        start_time = int(flask.request.args.get('start', ''))
        end_time = int(flask.request.args.get('end', ''))
        logger.info(f"Processing time range: {start_time} to {end_time}")
    except (TypeError, ValueError):
        logger.error("Invalid or missing time parameters.")
        raise ValueError('Invalid or missing start/end parameters.')

    if start_time < 0 or end_time < 0 or start_time >= end_time:
        logger.error("Invalid time range provided.")
        raise ValueError('Start time must be less than end time and non-negative.')

    return start_time, end_time