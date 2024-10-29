import dataclasses
import typing

@dataclasses.dataclass
class HoldModel:
    id: str = None
    bbox: typing.List[int] = dataclasses.field(default_factory=list)
    mask: typing.List[typing.List[int]] = dataclasses.field(default_factory=list)

    @classmethod
    def from_mongo(cls, mongo_hold):
        return cls(
            id=str(mongo_hold.id),
            bbox=[int(coord) for coord in mongo_hold.bbox],
            mask=mongo_hold.mask,
        )

    def asdict(self):
        return {
            'id': self.id,
            'bbox': self.bbox,
            'mask': self.mask,
        }

