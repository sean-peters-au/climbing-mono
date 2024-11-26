import typing
import sqlalchemy.orm

import betaboard.db.schema.route_schema as route_schema
import betaboard.db.schema.hold_schema as hold_schema
import betaboard.business.models.routes as routes_model
import betaboard.business.models.holds as holds_model
import betaboard.db.dao.base_dao as base_dao
import betaboard.db.dao.hold_dao as hold_dao

class RouteDAO:
    @staticmethod
    def _to_model(route: route_schema.RouteSchema) -> routes_model.RouteModel:
        hold_models = [hold_dao.HoldDAO._to_model(hold) for hold in route.holds]
        return routes_model.RouteModel(
            id=str(route.id),
            name=route.name,
            description=route.description,
            grade=route.grade,
            date=route.date,
            wall_id=str(route.wall_id),
            holds=hold_models,
        )

    @staticmethod
    @base_dao.with_session
    def get_all_routes(
        session: sqlalchemy.orm.Session
    ) -> typing.List[routes_model.RouteModel]:
        route_records = session.query(route_schema.RouteSchema).all()
        return [RouteDAO._to_model(route) for route in route_records]

    @staticmethod
    @base_dao.with_session
    def get_route_by_id(
        route_id: int,
        session: sqlalchemy.orm.Session
    ) -> routes_model.RouteModel:
        route = session.query(route_schema.RouteSchema).get(route_id)
        if route is None:
            raise ValueError("Route with given ID does not exist.")
        return RouteDAO._to_model(route)

    @staticmethod
    @base_dao.with_session
    def create_route(
        route_model: routes_model.RouteModel,
        session: sqlalchemy.orm.Session
    ) -> None:
        """
        Create a new route in the database.

        Args:
            route_model (RouteModel): The route model to create.
            session (sqlalchemy.orm.Session): The database session.
        """
        route = route_schema.RouteSchema(
            name=route_model.name,
            description=route_model.description,
            grade=route_model.grade,
            date=route_model.date,
            wall_id=int(route_model.wall_id)
        )
        session.add(route)

        # Associate holds
        hold_ids = [int(hold.id) for hold in route_model.holds if hold.id]
        route.holds = session.query(hold_schema.HoldSchema) \
            .filter(hold_schema.HoldSchema.id.in_(hold_ids)) \
            .all()

        session.flush()
        route_model.id = str(route.id)

    @staticmethod
    @base_dao.with_session
    def update_route(
        route_model: routes_model.RouteModel,
        session: sqlalchemy.orm.Session
    ) -> None:
        """
        Update an existing route in the database.

        Args:
            route_model (RouteModel): The route model with updated data.
            session (sqlalchemy.orm.Session): The database session.
        """
        route = session.query(route_schema.RouteSchema).get(int(route_model.id))
        if route is None:
            raise ValueError("Route with given ID does not exist.")

        route.name = route_model.name
        route.description = route_model.description
        route.grade = route_model.grade
        route.date = route_model.date
        route.wall_id = int(route_model.wall_id)

        # Update holds association
        hold_ids = [int(hold.id) for hold in route_model.holds if hold.id]
        route.holds = session.query(hold_schema.HoldSchema) \
            .filter(hold_schema.HoldSchema.id.in_(hold_ids)) \
            .all()

        session.flush()