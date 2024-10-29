import typing

import business.models.routes
import db.dao.route_dao
import db.dao.hold_dao
import db.dao.recording_dao

def get_route(route_id: str) -> business.models.routes.RouteModel:
    return db.dao.route_dao.RouteDAO.get_route_by_id(route_id)

def create_route(name: str, description: str, grade: str, date: str, hold_ids: typing.List[str]):
    hold_models = db.dao.hold_dao.HoldDAO.get_holds_by_ids(hold_ids)
    route_model = business.models.routes.RouteModel(
        name=name,
        description=description,
        grade=grade,
        date=date,
        holds=hold_models,
    )
    db.dao.route_dao.RouteDAO.save_route(route_model)
    return route_model

def get_route_recordings(route_id: str):
    return db.dao.recording_dao.RecordingDAO.get_recordings_by_route_id(route_id)
