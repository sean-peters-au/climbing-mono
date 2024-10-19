import dataclasses
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
    start_time: str
    end_time: str
    sensor_readings: typing.List[SensorReadingModel]

    @classmethod
    def from_mongo(cls, mongo_recording):
        return cls(
            id=str(mongo_recording.id),
            route_id=str(mongo_recording.route.id),
            start_time=mongo_recording.start_time.isoformat(),
            end_time=mongo_recording.end_time.isoformat(),
            sensor_readings=[
                SensorReadingModel.from_mongo(reading)
                for reading in mongo_recording.sensor_readings
            ],
        )

    def asdict(self):
        return dataclasses.asdict(self)