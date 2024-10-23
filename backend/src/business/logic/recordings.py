import concurrent.futures
import datetime
import json
from typing import List

import flask
import mongoengine.errors

import business.models.recordings
import business.logic.route
import db.schema

def create_recording(start_time: datetime.datetime, end_time: datetime.datetime, route_id: str):
    route = business.logic.route.get_route(route_id)

    # sensor_data = _get_sensor_data(start_time, end_time, route)
    sensor_reading_frames = _get_simulated_sensor_readings(start_time, end_time, route)

    sensor_readings_frames_db = [
        [
            db.schema.SensorReading(
                hold=sensor_reading['hold'],
                x=sensor_reading['x'],
                y=sensor_reading['y'],
            )
            for sensor_reading in sensor_reading_frame
        ]
        for sensor_reading_frame in sensor_reading_frames
    ]

    recording_db = db.schema.Recording(
        route=route.id,
        start_time=start_time,
        end_time=end_time,
        sensor_readings=sensor_readings_frames_db,
    )
    recording_db.save()

    return business.models.recordings.RecordingModel.from_mongo(recording_db)

def get_recording(recording_id):
    try:
        recording = db.schema.Recording.objects.get(id=recording_id)
    except mongoengine.errors.DoesNotExist:
        raise ValueError('Recording not found')

    return business.models.recordings.RecordingModel.from_mongo(recording)

def get_recordings(recording_ids: List[str]):
    recordings = db.schema.Recording.objects(id__in=recording_ids)
    return [business.models.recordings.RecordingModel.from_mongo(recording) for recording in recordings]

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

def _get_simulated_sensor_readings(
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    route: business.models.routes.RouteModel
):
    # read simulated sensors from file in
    # ./static/hold-vector-data/simulated-hold-{n}.json (there are only 5 simulated holds)
    simulated_sensor_readings = [
        json.load(open(f'./static/hold-vector-data/simulated-hold-{n}.json'))
        for n in range(1, 6)
    ]
    
    hold_ids = [hold.id for hold in route.holds]

    # pivot the simulated sensor readings so that each frame is a list of sensor readings from all holds
    n_frames = len(simulated_sensor_readings[0])
    sensor_reading_frames = []
    for i in range(n_frames):
        sensor_reading_frame = []
        for hold_id, simulated_sensor_reading in zip(hold_ids, simulated_sensor_readings):
            sensor_reading_frame.append({
                'hold': hold_id,
                'x': simulated_sensor_reading[i]['x'],
                'y': simulated_sensor_reading[i]['y'],
            })
        sensor_reading_frames.append(sensor_reading_frame)

    return sensor_reading_frames