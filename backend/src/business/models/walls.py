import dataclasses
import business.models.routes
import business.models.holds

@dataclasses.dataclass
class WallModel:
    id: str
    name: str
    height: int
    width: int
    image: str
    routes: list[business.models.routes.RouteModel]
    holds: list[business.models.holds.HoldModel]

    @classmethod
    def from_mongo(cls, mongo_wall):
        return cls(
            id=str(mongo_wall.id),
            name=mongo_wall.name,
            height=mongo_wall.height,
            width=mongo_wall.width,
            image=str(mongo_wall.image),
            routes=[business.models.routes.RouteModel.from_mongo(route) for route in mongo_wall.routes],
            holds=[business.models.holds.HoldModel.from_mongo(hold) for hold in mongo_wall.holds],
        )

    def asdict(self):
        return {
            'id': self.id,
            'name': self.name,
            'height': self.height,
            'width': self.width,
            'image': self.image,
            'routes': [route.asdict() for route in self.routes],
            'holds': [hold.asdict() for hold in self.holds],
        }
