from dataclasses import dataclass, asdict

@dataclass
class SegmentModel:
    bbox: list
    mask: list

    def asdict(self):
        return asdict(self)