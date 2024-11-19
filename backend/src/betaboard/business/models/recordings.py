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
    id: str
    route_id: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    sensor_readings: typing.List[typing.List[SensorReadingModel]]
    video_s3_key: str = None

    def asdict(self):
        return dataclasses.asdict(self)