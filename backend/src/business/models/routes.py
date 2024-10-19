import dataclasses

import business.models.holds

@dataclasses.dataclass
class RouteModel:
    id: str
    name: str
    description: str
    grade: str
    date: str
    holds: list[business.models.holds.HoldModel]

    @classmethod
    def from_mongo(cls, mongo_route):
        return cls(
            id=str(mongo_route.id),
            name=mongo_route.name,
            description=mongo_route.description,
            grade=mongo_route.grade,
            date=str(mongo_route.date),
            holds=[business.models.holds.HoldModel.from_mongo(hold) for hold in mongo_route.holds],
        )

    def asdict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'grade': self.grade,
            'date': self.date,
            'holds': [hold.asdict() for hold in self.holds],
        }
