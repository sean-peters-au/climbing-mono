import flask
import marshmallow

import betaboard.business.logic.sensors as sensors

sensor_bp = flask.Blueprint('sensor', __name__)

@sensor_bp.route('/sensor', methods=['POST'])
def create_sensor():
    class SensorSchema(marshmallow.Schema):
        name = marshmallow.fields.Str(required=True)
        ip_address = marshmallow.fields.Str(required=True)
        hold_id = marshmallow.fields.Str(required=True)

    try:
        data = SensorSchema().load(flask.request.json)
    except marshmallow.exceptions.ValidationError as err:
        return flask.jsonify(err.messages), 400

    sensor = sensors.add_sensor(data)

    return flask.jsonify(sensor), 201

@sensor_bp.route('/sensor/<id>', methods=['GET'])
def get_sensor(id):
    sensor = sensors.get_sensor(id)

    return flask.jsonify(sensor), 200

@sensor_bp.route('/sensor', methods=['GET'])
def get_sensors():
    sensors = sensors.get_sensors()

    return flask.jsonify(sensors), 200