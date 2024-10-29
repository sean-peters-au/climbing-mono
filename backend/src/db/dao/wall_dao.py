import typing

import business.models.walls
import business.models.holds
import db.dao.hold_dao
import db.dao.route_dao
import db.schema

class WallDAO:
    @staticmethod
    def get_all_walls() -> typing.List[business.models.walls.WallModel]:
        walls = db.schema.Wall.objects().all()
        return [business.models.walls.WallModel.from_mongo(wall) for wall in walls]

    @staticmethod
    def get_wall_by_id(wall_id: str) -> business.models.walls.WallModel:
        wall = db.schema.Wall.objects(id=wall_id).first().select_related()
        if not wall:
            raise ValueError("Wall with given ID does not exist.")
        return business.models.walls.WallModel.from_mongo(wall)

    @staticmethod
    def save_wall(wall_model: business.models.walls.WallModel):
        hold_schemas = [
            db.dao.hold_dao.HoldDAO.get_hold_schema_by_id(hold.id)
            for hold in wall_model.holds
        ]
        route_schemas = [
            db.dao.route_dao.RouteDAO.get_route_schema_by_id(route.id)
            for route in wall_model.routes
        ]
        wall_schema = db.schema.Wall(
            id=wall_model.id,
            name=wall_model.name,
            height=wall_model.height,
            width=wall_model.width,
            image=wall_model.image_id,
            holds=hold_schemas,
            routes=route_schemas,
        )
        wall_schema.save()
        wall_model.id = str(wall_schema.id)

    @staticmethod
    def add_hold_to_wall(wall_id: str, hold_model: business.models.holds.HoldModel):
        wall = db.schema.Wall.objects(id=wall_id).first()
        if not wall:
            raise ValueError("Wall with given ID does not exist.")
        db.dao.hold_dao.HoldDAO.save_hold(hold_model)
        wall.holds.append(hold_model.id)
        wall.save()
