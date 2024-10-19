import concurrent.futures
import datetime
import json

import flask
import mongoengine.errors

import business.models.recordings
import db.schema

def create_recording(start_time: datetime.datetime, end_time: datetime.datetime, route_id: str):
    route = db.schema.Route.objects.get(id=route_id)

    # sensor_data = _get_sensor_data(start_time, end_time, route)
    sensor_data = _get_simulated_sensor_data(start_time, end_time, route)

    sensor_readings = [
        db.schema.SensorReading(
            x=force_data[hold_id]['x'],
            y=force_data[hold_id]['y'],
        )
        for hold_id, force_data in sensor_data.items()
    ]

    recording = db.schema.Recording(
        route=route,
        start_time=start_time,
        end_time=end_time,
        sensor_readings=sensor_readings,
    )
    recording.save()

    return business.models.recordings.RecordingModel.from_mongo(recording)

def get_recording(recording_id):
    try:
        recording = db.schema.Recording.objects.get(id=recording_id)
    except mongoengine.errors.DoesNotExist:
        raise ValueError('Recording not found')

    return business.models.recordings.RecordingModel.from_mongo(recording)

def _get_sensor_data(start_time: datetime.datetime, end_time: datetime.datetime, route: db.schema.Route):
    sensors = db.schema.Sensor.objects(hold__in=route.holds)

    sensor_data = {
        sensor.hold.id: [
            flask.current_app.extensions['sensors'].get_sensor_force(
                sensor, start_time, end_time
            )
        ]
        for sensor in sensors
    }

    return sensor_data

def _get_simulated_sensor_data(start_time: datetime.datetime, end_time: datetime.datetime, route: db.schema.Route):
    sensors = db.schema.Sensor.objects(hold__in=route.holds)

    # read simulated sensors from file in
    # ./static/hold-vector-data/simulated-hold-{n}.json (there are only 5 simulated holds)
    simulated_sensors = [
        json.load(open(f'./static/hold-vector-data/simulated-hold-{n}.json'))
        for n in range(0, 5)
    ]

    sensor_data = {
        sensor.hold.id: simulated_sensor['force_data']
        for sensor, simulated_sensor in zip(sensors, simulated_sensors)
    }

    return sensor_data
