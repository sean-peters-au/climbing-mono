import datetime
import typing

import numpy as np

import business.models.recordings
import business.logic.route
import db.dao.recording_dao
import db.dao.route_dao

def create_recording(
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    route_id: str
) -> business.models.recordings.RecordingModel:
    route_model = db.dao.route_dao.RouteDAO.get_route_by_id(route_id)

    hold_ids = [hold.id for hold in route_model.holds]

    # Simulate the recording data
    sensor_reading_frames = _simulate_recording(start_time, end_time, hold_ids)

    recording_model = business.models.recordings.RecordingModel(
        id=None,
        route_id=route_id,
        start_time=start_time,
        end_time=end_time,
        sensor_readings=[
            [
                business.models.recordings.SensorReadingModel(
                    hold_id=sensor_reading['hold'],
                    x=sensor_reading['x'],
                    y=sensor_reading['y'],
                )
                for sensor_reading in frame
            ]
            for frame in sensor_reading_frames
        ],
    )

    db.dao.recording_dao.RecordingDAO.save_recording(recording_model)

    return recording_model

def get_recording(recording_id: str) -> business.models.recordings.RecordingModel:
    return db.dao.recording_dao.RecordingDAO.get_recording_by_id(recording_id)

def get_recordings(recording_ids: typing.List[str]) -> typing.List[business.models.recordings.RecordingModel]:
    return db.dao.recording_dao.RecordingDAO.get_recordings_by_ids(recording_ids)

def _generate_smooth_load(duration_seconds, sample_rate, negative_mean=True):
    num_samples = int(duration_seconds * sample_rate)
    time = np.linspace(0, duration_seconds, num_samples)

    # Generate base load with some randomness
    mean_load = -300 if negative_mean else 0
    base_load = np.random.normal(loc=mean_load, scale=50, size=num_samples)

    # Smooth the load with a moving average
    window_size = 5
    smoothed_load = np.convolve(
        base_load,
        np.ones(window_size) / window_size,
        mode='same'
    )

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

def _simulate_recording(start_time: datetime.datetime, end_time: datetime.datetime, hold_ids: typing.List[str], sample_rate=10):
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

