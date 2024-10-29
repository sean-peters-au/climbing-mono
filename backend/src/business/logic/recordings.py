import datetime
import json
from typing import List

import flask
import mongoengine.errors
import numpy as np

import business.models.recordings
import business.logic.route
import db.schema

def create_recording(start_time: datetime.datetime, end_time: datetime.datetime, route_id: str):
    route = business.logic.route.get_route(route_id)

    # sensor_data = _get_sensor_data(start_time, end_time, route)
    hold_ids = [hold.id for hold in route.holds]
    sensor_reading_frames = _simulate_recording(start_time, end_time, hold_ids)

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
            print(i)
            sensor_reading_frame.append({
                'hold': hold_id,
                'x': simulated_sensor_reading[i]['x'],
                'y': simulated_sensor_reading[i]['y'],
            })
        sensor_reading_frames.append(sensor_reading_frame)

    return sensor_reading_frames



import datetime
import numpy as np
from typing import List

def _generate_smooth_load(duration_seconds, sample_rate, negative_mean=True):
    num_samples = int(duration_seconds * sample_rate)
    time = np.linspace(0, duration_seconds, num_samples)

    # Generate base load with some randomness
    mean_load = -300 if negative_mean else 0
    base_load = np.random.normal(loc=mean_load, scale=50, size=num_samples)

    # Smooth it out with a moving average
    window_size = 5
    smoothed_load = np.convolve(base_load, np.ones(window_size)/window_size, mode='same')

    # Add small random variations
    noise = np.random.normal(0, 10, num_samples)
    final_load = smoothed_load + noise

    return final_load

def _simulate_hold_data(duration, sample_rate):
    num_samples = int(duration * sample_rate)

    # Generate y (vertical load), typically negative (downward force)
    y_load = _generate_smooth_load(duration, sample_rate, negative_mean=True)

    # Generate x (horizontal load), smaller than vertical, can be positive or negative
    x_load = _generate_smooth_load(duration, sample_rate, negative_mean=False) * 0.3

    # Create hold data as list of dicts
    hold_data = [{"x": round(x, 2), "y": round(y, 2)} for x, y in zip(x_load, y_load)]

    return hold_data

def _simulate_recording(start_time: datetime.datetime, end_time: datetime.datetime, hold_ids: List[str], sample_rate=10):
    duration = (end_time - start_time).total_seconds()
    num_samples = int(duration * sample_rate)

    sensor_reading_frames = []

    num_holds = len(hold_ids)
    hold_timings = []
    current_time = 0.0

    # Determine when each hold is grabbed and released
    # Holds are used in order, overlapping to maintain 3-4 holds at a time
    for hold_index in range(num_holds):
        # Each hold is held for a random duration between 2 to 5 seconds
        hold_duration = np.random.uniform(2, 5)
        hold_start_time = current_time
        hold_end_time = hold_start_time + hold_duration
        hold_timings.append((hold_ids[hold_index], hold_start_time, hold_end_time))
        current_time += np.random.uniform(1, 3)  # Time before grabbing next hold

    # Ensure total duration is covered
    max_time = max(end_time.timestamp(), current_time)
    total_frames = int((max_time - start_time.timestamp()) * sample_rate)

    # For each frame, determine active holds and generate sensor readings
    for frame_index in range(total_frames):
        frame_time = start_time.timestamp() + frame_index / sample_rate
        frame_readings = []

        # Find active holds at this time
        active_holds = [
            hold_id for hold_id, hold_start, hold_end in hold_timings
            if hold_start <= frame_time - start_time.timestamp() <= hold_end
        ]

        # Ensure 3-4 holds are active
        if len(active_holds) < 3:
            # Add next holds to ensure at least 3 holds are active
            next_hold_indices = [i for i, (_, hold_start, _) in enumerate(hold_timings)
                                 if hold_start > frame_time - start_time.timestamp()]
            for idx in next_hold_indices:
                if hold_timings[idx][0] not in active_holds:
                    active_holds.append(hold_timings[idx][0])
                if len(active_holds) >= 3:
                    break

        # Generate sensor data for each hold
        for hold_id in hold_ids:
            if hold_id in active_holds:
                # Simulate hold data for this frame
                hold_data = _simulate_hold_data(duration=1/sample_rate, sample_rate=sample_rate)[0]
            else:
                # No load on this hold
                hold_data = {"x": 0.0, "y": 0.0}

            frame_readings.append({
                'hold': hold_id,
                'x': hold_data['x'],
                'y': hold_data['y'],
            })

        sensor_reading_frames.append(frame_readings)

    return sensor_reading_frames
