import dataclasses
import typing

import betaboard.business.models.holds as holds_model

@dataclasses.dataclass
class RouteModel:
    id: str = None
    name: str = ""
    description: str = ""
    grade: str = ""
    date: str = ""
    wall_id: int = None
    holds: typing.List[holds_model.HoldModel] = dataclasses.field(default_factory=list)

    def asdict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'grade': self.grade,
            'date': self.date,
            'wall_id': self.wall_id,
            'holds': [hold.asdict() for hold in self.holds],
        }
