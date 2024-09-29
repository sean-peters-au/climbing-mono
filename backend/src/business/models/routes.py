import dataclasses

@dataclasses.dataclass
class RouteModel:
    id: str
    name: str
    description: str
    grade: str
    date: str
    holds: list  # List of hold IDs

    @classmethod
    def from_mongo(cls, mongo_data):
        return cls(
            id=str(mongo_data['_id']),
            name=mongo_data.get('name', ''),
            description=mongo_data.get('description', ''),
            grade=mongo_data.get('grade', ''),
            date=str(mongo_data.get('date', '')),
            holds=[str(hold_id) for hold_id in mongo_data['holds']],
        )

    def asdict(self):
        return dataclasses.asdict(self)
