import dataclasses
import typing
import business.models.routes
import business.models.holds

@dataclasses.dataclass
class WallModel:
    id: str = None
    name: str = ""
    height: int = 0
    width: int = 0
    image_id: str = ""
    image_url: str = ""
    routes: typing.List[business.models.routes.RouteModel] = dataclasses.field(default_factory=list)
    holds: typing.List[business.models.holds.HoldModel] = dataclasses.field(default_factory=list)

    @classmethod
    def from_mongo(cls, mongo_wall):
        hold_models = [
            business.models.holds.HoldModel.from_mongo(hold)
            for hold in mongo_wall.holds
        ]
        route_models = [
            business.models.routes.RouteModel.from_mongo(route)
            for route in mongo_wall.routes
        ]
        return cls(
            id=str(mongo_wall.id),
            name=mongo_wall.name,
            height=mongo_wall.height,
            width=mongo_wall.width,
            image_id=str(mongo_wall.image),
            routes=route_models,
            holds=hold_models,
        )

    def asdict(self):
        return {
            'id': self.id,
            'name': self.name,
            'height': self.height,
            'width': self.width,
            'image_id': self.image_id,
            'image_url': self.image_url,
            'routes': [route.asdict() for route in self.routes],
            'holds': [hold.asdict() for hold in self.holds],
        }
