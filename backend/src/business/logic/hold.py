import typing
import business.models.holds
import db.dao.hold_dao
import services.imaging_service


def create_hold_from_segment(segment: services.imaging_service.Segment):
    hold_model = business.models.holds.HoldModel(
        bbox=segment.bbox,
        mask=segment.mask,
    )
    db.dao.hold_dao.HoldDAO.save_hold(hold_model)
    return hold_model

def get_hold(hold_id: str) -> business.models.holds.HoldModel:
    return db.dao.hold_dao.HoldDAO.get_hold_by_id(hold_id)

def get_holds() -> typing.List[business.models.holds.HoldModel]:
    return db.dao.hold_dao.HoldDAO.get_all_holds()
