import logging

import flask

import betaboard_camera.routes
import betaboard_camera.utils.config as config_utils


def setup_logging() -> logging.Logger:
    """
    Configure and return the logger for the application.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger('betaboard_camera')
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def create_app() -> flask.Flask:
    """
    Create and configure the Flask application.

    Returns:
        flask.Flask: Configured Flask application.
    """
    app = flask.Flask(__name__)
    app.config.from_object(config_utils.Config)
    setup_logging()
    betaboard_camera.routes.init_app(app)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000)