import dataclasses
import typing
import business.models.holds

@dataclasses.dataclass
class RouteModel:
    id: str = None
    name: str = ""
    description: str = ""
    grade: str = ""
    date: str = ""
    holds: typing.List[business.models.holds.HoldModel] = dataclasses.field(default_factory=list)

    @classmethod
    def from_mongo(cls, mongo_route):
        hold_models = [
            business.models.holds.HoldModel.from_mongo(hold)
            for hold in mongo_route.holds
        ]
        return cls(
            id=str(mongo_route.id),
            name=mongo_route.name,
            description=mongo_route.description,
            grade=mongo_route.grade,
            date=str(mongo_route.date),
            holds=hold_models,
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
