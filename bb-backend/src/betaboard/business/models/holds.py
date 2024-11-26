import dataclasses
import typing

@dataclasses.dataclass
class HoldModel:
    id: str = None
    bbox: typing.List[int] = dataclasses.field(default_factory=list)
    mask: typing.List[typing.List[int]] = dataclasses.field(default_factory=list)

    def asdict(self):
        return {
            'id': self.id,
            'bbox': self.bbox,
            'mask': self.mask,
        }
