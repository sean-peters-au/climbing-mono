import dataclasses
import db.schema

import services.imaging_service

@dataclasses.dataclass
class HoldModel:
    id: str
    bbox: list
    mask: list

    @classmethod
    def from_mongo(cls, mongo_hold):
        # Ensure that bbox is a list of integers
        bbox = [int(coord) for coord in mongo_hold.bbox]
        # Ensure mask is a list of lists of 0s and 1s
        mask = None
        if mongo_hold.mask is not None:
            mask = [[1 if value else 0 for value in row] for row in mongo_hold.mask]
        return cls(
            id=str(mongo_hold.id),
            bbox=bbox,
            mask=mask,
        )

    def asdict(self):
        return {
            'id': self.id,
            'bbox': self.bbox,
            'mask': self.mask,
        }

def create_hold_from_segment(segment: services.imaging_service.Segment):
    hold = db.schema.Hold(
        bbox=segment.bbox,
        mask=segment.mask,
    )
    print(f'hold.mask: {hold.mask}')
    hold.save()
    return hold

