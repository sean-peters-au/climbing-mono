import datetime
import io
import typing

import numpy as np
import flask

import betaboard.business.models.recordings as recordings_model
import betaboard.db.dao.recording_dao as recording_dao
import betaboard.db.dao.route_dao as route_dao
import betaboard.db.dao.hold_dao as hold_dao

def create_recording(
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    route_id: str
) -> recordings_model.RecordingModel:
    """
    Creates a new recording for a route.

    :param start_time: The start time of the recording.
    :param end_time: The end time of the recording.
    :param route_id: The ID of the route.
    :return: The created recording model.
    """
    route_model = route_dao.RouteDAO.get_route_by_id(route_id)
    hold_ids = [hold.id for hold in route_model.holds]

    # Simulate the recording data
    sensor_reading_frames = _simulate_recording(start_time, end_time, hold_ids)

    # Get the camera service client and S3 client
    camera_client = flask.current_app.extensions['camera_service']
    s3_client = flask.current_app.extensions['s3']

    # Fetch video from camera service
    start_timestamp = int(start_time.timestamp())
    end_timestamp = int(end_time.timestamp())

    video_data = camera_client.get_video(start=start_timestamp, end=end_timestamp)

    # Upload video to S3
    video_file = io.BytesIO(video_data)
    s3_key = s3_client.upload_file(video_file)
    print(f"Uploaded video to S3 with key: {s3_key}")
    print(f"Video url: {s3_client.get_presigned_url(s3_key)}")

    # Create the recording model
    recording_model = recordings_model.RecordingModel(
        id=None,
        route_id=route_id,
        start_time=start_time,
        end_time=end_time,
        sensor_readings=[
            [
                recordings_model.SensorReadingModel(
                    hold_id=sensor_reading['hold'],
                    x=sensor_reading['x'],
                    y=sensor_reading['y'],
                )
                for sensor_reading in frame
            ]
            for frame in sensor_reading_frames
        ],
        video_s3_key=s3_key
    )

    # Save the recording
    recording_dao.RecordingDAO.save_recording(recording_model)

    return recording_model

def get_recording(recording_id: str) -> recordings_model.RecordingModel:
    return recording_dao.RecordingDAO.get_recording_by_id(recording_id)

def get_recordings(recording_ids: typing.List[str]) -> typing.List[recordings_model.RecordingModel]:
    return recording_dao.RecordingDAO.get_recordings_by_ids(recording_ids)

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
    holds = hold_dao.HoldDAO.get_holds_by_ids(hold_ids)

    sensor_reading_frames = []

    hold_timings = []
    current_time = 0.0

    # Start with the lowest hold
    holds_dict = {hold.id: hold for hold in holds}
    first_hold_id = max(hold_ids, key=lambda hold_id: holds_dict[hold_id].bbox[1])
    ordered_holds = [first_hold_id]
    remaining_holds = set(hold_ids) - {first_hold_id}

    # Helper function to calculate distance between holds
    def get_hold_distance(hold1_id: str, hold2_id: str) -> float:
        hold1 = holds_dict[hold1_id]
        hold2 = holds_dict[hold2_id]
        # Using center points of holds for distance calculation
        x1 = hold1.bbox[0] + hold1.bbox[2] / 2
        y1 = hold1.bbox[1] + hold1.bbox[3] / 2
        x2 = hold2.bbox[0] + hold2.bbox[2] / 2
        y2 = hold2.bbox[1] + hold2.bbox[3] / 2
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    # Order remaining holds by distance from the last added hold
    while remaining_holds:
        last_hold = ordered_holds[-1]
        next_hold = min(
            remaining_holds,
            key=lambda hold_id: get_hold_distance(last_hold, hold_id)
        )
        ordered_holds.append(next_hold)
        remaining_holds.remove(next_hold)

    # Use ordered_holds for timing simulation
    for hold_index in range(len(ordered_holds)):
        hold_duration = np.random.uniform(0.5, 2)
        hold_start_time = current_time
        hold_end_time = hold_start_time + hold_duration
        hold_timings.append((ordered_holds[hold_index], hold_start_time, hold_end_time))
        current_time += np.random.uniform(0.5, 1.5)  # Time before grabbing next hold

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

