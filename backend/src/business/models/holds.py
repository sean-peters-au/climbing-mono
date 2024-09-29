import collections
import dataclasses
import db.schema

collections.namedtuple('Segment', ['bbox', 'mask'])

@dataclasses.dataclass
class HoldModel:
    id: str
    bbox: list
    mask: list

    @classmethod
    def from_mongo(cls, mongo_data):
        return cls(
            id=str(mongo_data['_id']),
            bbox=mongo_data['bbox'],
            mask=mongo_data['mask'],
        )

    def asdict(self):
        return dataclasses.asdict(self)

def create_hold(segment):
    hold = db.schema.Hold(**segment)
    hold.save()
    return hold

