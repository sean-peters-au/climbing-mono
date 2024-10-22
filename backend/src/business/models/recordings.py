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

    @classmethod
    def from_mongo(cls, mongo_recording):
        return cls(
            id=str(mongo_recording.id),
            route_id=str(mongo_recording.route.id),
            start_time=mongo_recording.start_time,
            end_time=mongo_recording.end_time,
            sensor_readings=[
                [SensorReadingModel.from_mongo(reading)
                for reading in sensor_reading_frame]
                for sensor_reading_frame in mongo_recording.sensor_readings
            ],
        )

    def asdict(self):
        return dataclasses.asdict(self)