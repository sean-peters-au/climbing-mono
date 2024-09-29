import dataclasses
import datetime

import business.models.holds
import db.schema

@dataclasses.dataclass
class RecordingModel:
    id: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    climb_id: str
    holds: list[business.models.holds.HoldModel]

    @classmethod
    def from_mongo(cls, mongo_data):
        return cls(
            id=str(mongo_data['_id']),
            start_time=mongo_data['start_time'],
            end_time=mongo_data['end_time'],
            climb_id=mongo_data['climb_id'],
            holds=[business.models.holds.HoldModel.from_mongo(hold) for hold in mongo_data['holds']],
        )

    def asdict(self):
        return dataclasses.asdict(self)