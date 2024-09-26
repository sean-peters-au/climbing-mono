from dataclasses import dataclass, asdict
import db.schema

@dataclass
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
        return asdict(self)

def create_hold(hold_model):
    hold = db.schema.Hold(**hold_model)
    hold.save()
    return hold

