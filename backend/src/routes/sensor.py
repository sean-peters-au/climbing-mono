import flask
import marshmallow

from . import api_bp

@api_bp.route('/sensor', methods=['POST'])
def create_sensor():
    class SensorSchema(marshmallow.Schema):
        name = marshmallow.fields.Str(required=True)
        ip_address = marshmallow.fields.Str(required=True)
        hold_id = marshmallow.fields.Str(required=True)

    try:
        data = SensorSchema().load(flask.request.json)
    except marshmallow.exceptions.ValidationError as err:
        return flask.jsonify(err.messages), 400

    sensor = business.logic.sensor.create_sensor(data)

    return flask.jsonify(sensor), 201

@api_bp.route('/sensor/<id>', methods=['GET'])
def get_sensor(id):
    sensor = business.logic.sensor.get_sensor(id)

    return flask.jsonify(sensor), 200

@api_bp.route('/sensor', methods=['GET'])
def get_sensors():
    sensors = business.logic.sensor.get_sensors()

    return flask.jsonify(sensors), 200