import datetime
import io
import typing

import flask
import numpy as np

import betaboard.business.models.recordings as recordings_model
import betaboard.db.dao.recording_dao as recording_dao
import betaboard.db.dao.route_dao as route_dao
import betaboard.db.dao.hold_dao as hold_dao


def start_recording(route_id: str) -> recordings_model.RecordingModel:
    """
    Start recording a climbing attempt.

    Args:
        route_id: ID of the route being climbed.

    Returns:
        RecordingModel: The created recording model.

    Raises:
        ValueError: If route doesn't exist or camera service fails.
    """
    # Verify route exists
    route_dao.RouteDAO.get_route_by_id(route_id)

    # Get camera service
    camera_client = flask.current_app.extensions['camera_service']

    # Start recording on camera
    if not camera_client.start_recording():
        raise ValueError("Failed to start camera recording")

    # Create recording entry
    recording_model = recording_dao.RecordingDAO.create_recording(
        route_id=route_id,
        start_time=datetime.datetime.utcnow()
    )

    return recording_model


def stop_recording(recording_id: str) -> recordings_model.RecordingModel:
    """
    Stop recording a climbing attempt, save the video, and generate sensor data.

    Args:
        recording_id (str): The ID of the recording to stop.

    Returns:
        RecordingModel: The updated recording model.

    Raises:
        ValueError: If recording not found or services fail.
    """
    # Generate simulated sensor data
    end_time = datetime.datetime.now(datetime.timezone.utc)

    # Get the current recording
    recording = recording_dao.RecordingDAO.get_recording_by_id(recording_id)
    
    # Get services
    camera_client = flask.current_app.extensions['camera_service']
    s3_client = flask.current_app.extensions['s3']

    try:
        # Stop recording and get video data
        video_data = camera_client.stop_recording()

        # Upload video to S3
        video_file = io.BytesIO(video_data)
        s3_key = s3_client.upload_file(video_file)

        # Get route and hold information for sensor simulation
        route_model = route_dao.RouteDAO.get_route_by_id(recording.route_id)
        hold_ids = [hold.id for hold in route_model.holds]

        sensor_reading_frames = _simulate_recording(recording.start_time, end_time, hold_ids)

        # Transform sensor readings to SensorReadingModel instances
        sensor_readings_models = [
            [
                recordings_model.SensorReadingModel(
                    hold_id=sensor_reading['hold_id'],
                    x=sensor_reading['x'],
                    y=sensor_reading['y'],
                )
                for sensor_reading in frame
            ]
            for frame in sensor_reading_frames
        ]

        # Update recording with all data
        recording_model = recording_dao.RecordingDAO.update_recording(
            recording_id=recording_id,
            end_time=end_time,
            video_s3_key=s3_key,
            status='completed',
            sensor_readings=sensor_readings_models
        )

        return recording_model

    except Exception as e:
        # Mark recording as failed if something goes wrong
        recording_dao.RecordingDAO.update_recording(
            recording_id=recording_id,
            status='failed'
        )
        raise ValueError(f"Failed to stop recording: {str(e)}")


def get_recording(recording_id: str) -> recordings_model.RecordingModel:
    """Get a specific recording."""
    return recording_dao.RecordingDAO.get_recording_by_id(recording_id)

def get_recordings(recording_ids: typing.List[str]) -> typing.List[recordings_model.RecordingModel]:
    """Get multiple recordings by their IDs."""
    return recording_dao.RecordingDAO.get_recordings_by_ids(recording_ids)

def get_recording_video_url(recording_id: str) -> str:
    """Get the video URL for a recording."""
    recording = recording_dao.RecordingDAO.get_recording_by_id(recording_id)
    s3_client = flask.current_app.extensions['s3']
    return s3_client.get_file_url(recording.video_s3_key)

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

def _simulate_recording(
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    hold_ids: typing.List[str],
    sample_rate=10
) -> typing.List[typing.List[dict]]:
    """
    Simulates sensor readings for a recording.

    Returns sensor readings as a list of frames, where each frame is a list of dictionaries
    containing 'hold_id', 'x', and 'y'.

    Args:
        start_time: The start time of the recording.
        end_time: The end time of the recording.
        hold_ids: List of hold IDs involved in the route.
        sample_rate: The sample rate for sensor readings.

    Returns:
        List[List[dict]]: Simulated sensor readings.
    """
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
                'hold_id': hold_id,
                'x': hold_data['x'],
                'y': hold_data['y'],
            })

        sensor_reading_frames.append(frame_readings)

    return sensor_reading_frames

