import concurrent.futures
import datetime

import flask
import mongoengine.errors

import business.models.recordings
import db.schema

def stop_recording(recording_id):
    if not recording_id:
        raise ValueError('recording_id is required')

    try:
        recording = db.schema.Recording.objects.get(id=recording_id)
    except mongoengine.errors.DoesNotExist:
        raise ValueError('Recording not found')

    recording.end_time = datetime.datetime.utcnow()

    sensor_data = []
    sensors = db.schema.Sensor.objects(hold__in=recording.climb.holds)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        sensor_data.extend(executor.map(
            lambda sensor: flask.current_app.extensions['sensors'].get_sensor_force(sensor, recording),
            sensors
        ))

    recording.sensor_data = sensor_data
    recording.save()

    # Convert to RecordingModel
    recording_model = business.models.recordings.RecordingModel.from_mongo(recording.to_mongo())

    return recording_model

def get_recording_forces(recording_id):
    try:
        recording = db.schema.Recording.objects.get(id=recording_id)
    except mongoengine.errors.DoesNotExist:
        raise ValueError('Recording not found')

    # Convert to RecordingModel
    recording_model = business.models.recordings.RecordingModel.from_mongo(recording.to_mongo())

    return recording_model