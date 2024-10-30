import dataclasses
import datetime
import typing

@dataclasses.dataclass
class SensorReadingModel:
    hold_id: str
    x: float
    y: float

    @classmethod
    def from_mongo(cls, mongo_force_data):
        return cls(
            hold_id=str(mongo_force_data.hold.id),
            x=mongo_force_data.x,
            y=mongo_force_data.y,
        )

@dataclasses.dataclass
class RecordingModel:
    id: str
    route_id: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    sensor_readings: typing.List[typing.List[SensorReadingModel]]

    def asdict(self):
        return dataclasses.asdict(self)