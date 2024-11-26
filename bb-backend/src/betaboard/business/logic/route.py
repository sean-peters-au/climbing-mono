import typing

import betaboard.business.models.routes as routes_model
import betaboard.db.dao.route_dao as route_dao
import betaboard.db.dao.hold_dao as hold_dao
import betaboard.db.dao.recording_dao as recording_dao

def get_route(route_id: str) -> routes_model.RouteModel:
    return route_dao.RouteDAO.get_route_by_id(route_id)

def create_route(name: str, description: str, grade: str, date: str, hold_ids: typing.List[str]):
    hold_models = hold_dao.HoldDAO.get_holds_by_ids(hold_ids)
    route_model = routes_model.RouteModel(
        name=name,
        description=description,
        grade=grade,
        date=date,
        holds=hold_models,
    )
    route_dao.RouteDAO.save_route(route_model)
    return route_model

def get_route_recordings(route_id: str):
    return recording_dao.RecordingDAO.get_recordings_by_route_id(route_id)
