import dataclasses
import typing

import betaboard.business.models.routes as routes_model
import betaboard.business.models.holds as holds_model

@dataclasses.dataclass
class WallModel:
    id: str = None
    name: str = ""
    height: int = 0
    width: int = 0
    image_id: str = ""
    image_url: str = ""
    routes: typing.List[routes_model.RouteModel] = dataclasses.field(default_factory=list)
    holds: typing.List[holds_model.HoldModel] = dataclasses.field(default_factory=list)

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
