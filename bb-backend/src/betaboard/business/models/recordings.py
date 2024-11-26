import dataclasses
import datetime
import typing

@dataclasses.dataclass
class SensorReadingModel:
    hold_id: str
    x: float
    y: float

@dataclasses.dataclass
class RecordingModel:
    """
    Model representing a climbing recording.

    Args:
        id: Unique identifier for the recording
        route_id: ID of the route being climbed
        start_time: When the recording started
        end_time: When the recording ended (None if still recording)
        sensor_readings: List of sensor readings per frame
        video_s3_key: S3 key for the stored video (None if still recording)
        status: Current status of the recording ('recording', 'completed', or 'failed')
    """
    id: str
    route_id: str
    start_time: datetime.datetime
    end_time: typing.Optional[datetime.datetime]
    sensor_readings: typing.List[typing.List[SensorReadingModel]]
    video_s3_key: typing.Optional[str] = None
    status: str = 'recording'

    def asdict(self) -> dict:
        """Convert the model to a dictionary."""
        return dataclasses.asdict(self)
