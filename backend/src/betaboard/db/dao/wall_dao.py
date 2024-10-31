import typing
import sqlalchemy.orm

import betaboard.db.schema.wall_schema as wall_schema
import betaboard.db.schema.hold_schema as hold_schema
import betaboard.business.models.walls as walls_model
import betaboard.db.dao.base_dao as base_dao
import betaboard.db.dao.hold_dao as hold_dao
import betaboard.db.dao.route_dao as route_dao

class WallDAO:
    @staticmethod
    def _load_relationships():
        return [
            sqlalchemy.orm.joinedload(wall_schema.WallSchema.holds),
            sqlalchemy.orm.joinedload(wall_schema.WallSchema.routes),
        ]

    @staticmethod
    def _to_model(wall: wall_schema.WallSchema) -> walls_model.WallModel:
        hold_models = [hold_dao.HoldDAO._to_model(hold) for hold in wall.holds]
        route_models = [route_dao.RouteDAO._to_model(route) for route in wall.routes]
        return walls_model.WallModel(
            id=str(wall.id),
            name=wall.name,
            height=wall.height,
            width=wall.width,
            image_id=wall.image_id,
            holds=hold_models,
            routes=route_models,
        )

    @staticmethod
    @base_dao.with_session
    def create_wall(
        wall_model: walls_model.WallModel,
        session: sqlalchemy.orm.Session
    ):
        wall = wall_schema.WallSchema(
            name=wall_model.name,
            height=wall_model.height,
            width=wall_model.width,
            image_id=wall_model.image_id,
        )

        # Associate holds
        hold_ids = [int(hold.id) for hold in wall_model.holds if hold.id]
        wall.holds = session.query(hold_schema.HoldSchema) \
            .filter(hold_schema.HoldSchema.id.in_(hold_ids)) \
            .all()

        session.add(wall)
        session.flush()

        # Reload the wall with all relationships
        wall = session.query(wall_schema.WallSchema) \
            .options(*WallDAO._load_relationships()) \
            .get(wall.id)

        # Update the model with the new ID
        wall_model.id = str(wall.id)

    @staticmethod
    @base_dao.with_session
    def update_wall(
        wall_model: walls_model.WallModel,
        session: sqlalchemy.orm.Session
    ) -> None:
        """
        Update a wall's details in the database.

        Args:
            wall_model (WallModel): The wall model with updated data.
            session (Session): The database session.
        """
        wall = session.query(wall_schema.WallSchema) \
            .options(*WallDAO._load_relationships()) \
            .get(int(wall_model.id))

        if wall is None:
            raise ValueError("Wall with given ID does not exist.")

        wall.name = wall_model.name
        wall.height = wall_model.height
        wall.width = wall_model.width
        wall.image_id = wall_model.image_id

        # Update holds association
        hold_ids = [int(hold.id) for hold in wall_model.holds if hold.id]
        wall.holds = session.query(hold_schema.HoldSchema) \
            .filter(hold_schema.HoldSchema.id.in_(hold_ids)) \
            .all()

        session.flush()

    @staticmethod
    @base_dao.with_session
    def get_wall_by_id(
        wall_id: int,
        session: sqlalchemy.orm.Session
    ) -> walls_model.WallModel:
        wall = session.query(wall_schema.WallSchema) \
            .options(*WallDAO._load_relationships()) \
            .get(wall_id)

        if wall is None:
            raise ValueError("Wall with given ID does not exist.")

        return WallDAO._to_model(wall)

    @staticmethod
    @base_dao.with_session
    def get_all_walls(
        session: sqlalchemy.orm.Session
    ) -> typing.List[walls_model.WallModel]:
        wall_records = session.query(wall_schema.WallSchema) \
            .options(*WallDAO._load_relationships()) \
            .all()
        return [WallDAO._to_model(wall) for wall in wall_records]
