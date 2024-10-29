import typing
import db.schema
import business.models.routes
import business.models.holds

class RouteDAO:
    @staticmethod
    def get_all_routes() -> typing.List[business.models.routes.RouteModel]:
        routes = db.schema.Route.objects().all()
        return [business.models.routes.RouteModel.from_mongo(route) for route in routes]

    @staticmethod
    def get_route_by_id(route_id: str) -> business.models.routes.RouteModel:
        route = db.schema.Route.objects(id=route_id).first()
        if not route:
            raise ValueError("Route with given ID does not exist.")
        return business.models.routes.RouteModel.from_mongo(route)

    @staticmethod
    def save_route(route_model: business.models.routes.RouteModel):
        hold_schemas = db.schema.Hold.objects(id__in=[hold.id for hold in route_model.holds])
        route_schema = db.schema.Route(
            name=route_model.name,
            description=route_model.description,
            grade=route_model.grade,
            date=route_model.date,
            holds=hold_schemas,
        )
        route_schema.save()
        route_model.id = str(route_schema.id)