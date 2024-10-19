import logging

import flask

def init_logging(app):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    @app.before_request
    def before_request():
        flask.g.logger = logger

def logger():
    return flask.g.logger