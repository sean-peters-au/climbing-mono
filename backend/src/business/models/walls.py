import dataclasses

@dataclasses.dataclass
class WallModel:
    id: str
    name: str
    height: int
    width: int
    image: str
    routes: list
    holds: list

    @classmethod
    def from_mongo(cls, mongo_data):
        return cls(
            id=str(mongo_data['_id']),
            name=mongo_data['name'],
            height=mongo_data['height'],
            width=mongo_data['width'],
            image=mongo_data['image'],
            routes=[str(route_id) for route_id in mongo_data['routes']],
            holds=[str(hold_id) for hold_id in mongo_data['holds']],
        )

    def asdict(self):
        return dataclasses.asdict(self)
