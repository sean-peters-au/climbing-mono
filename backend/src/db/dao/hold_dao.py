import typing

import db.schema
import business.models.holds

class HoldDAO:
    @staticmethod
    def get_all_holds() -> typing.List[business.models.holds.HoldModel]:
        holds = db.schema.Hold.objects().all()
        return [business.models.holds.HoldModel.from_mongo(hold) for hold in holds]

    @staticmethod
    def get_hold_by_id(hold_id: str) -> business.models.holds.HoldModel:
        hold = db.schema.Hold.objects(id=hold_id).first()
        if not hold:
            raise ValueError("Hold with given ID does not exist.")
        return business.models.holds.HoldModel.from_mongo(hold)

    @staticmethod
    def get_holds_by_ids(hold_ids: typing.List[str]) -> typing.List[business.models.holds.HoldModel]:
        holds = db.schema.Hold.objects(id__in=hold_ids).all()
        return [business.models.holds.HoldModel.from_mongo(hold) for hold in holds]

    @staticmethod
    def get_hold_schema_by_id(hold_id: str) -> db.schema.Hold:
        hold = db.schema.Hold.objects(id=hold_id).first()
        if not hold:
            raise ValueError("Hold with given ID does not exist.")
        return hold

    @staticmethod
    def save_hold(hold_model: business.models.holds.HoldModel):
        hold_schema = db.schema.Hold(
            id=hold_model.id,
            bbox=hold_model.bbox,
            mask=hold_model.mask,
        )
        hold_schema.save()
        hold_model.id = str(hold_schema.id)