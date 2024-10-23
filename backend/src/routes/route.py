import flask

import business.logic.route

routes_bp = flask.Blueprint('routes', __name__)

@routes_bp.route('/routes/<id>/recordings', methods=['GET'])
def get_route_recordings(id):
    recordings = business.logic.route.get_route_recordings(id)

    return flask.jsonify({
        'recordings': [recording.asdict() for recording in recordings]
    }), 200
