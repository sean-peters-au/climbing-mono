import typing

import betaboard.business.models.holds as holds_model
import betaboard.db.dao.hold_dao as hold_dao
import betaboard.services.imaging_service as imaging_service


def create_hold_from_segment(segment: imaging_service.Segment):
    hold_model = holds_model.HoldModel(
        bbox=segment.bbox,
        mask=segment.mask,
    )
    hold_dao.HoldDAO.save_hold(hold_model)
    return hold_model

def get_hold(hold_id: str) -> holds_model.HoldModel:
    return hold_dao.HoldDAO.get_hold_by_id(hold_id)

def get_holds() -> typing.List[holds_model.HoldModel]:
    return hold_dao.HoldDAO.get_all_holds()
