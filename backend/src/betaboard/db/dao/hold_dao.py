import typing
import zlib
import json
import sqlalchemy.orm

import betaboard.db.schema.hold_schema as hold_schema
import betaboard.business.models.holds as holds
import betaboard.db.dao.base_dao as base_dao

class HoldDAO:
    @staticmethod
    def _compress_mask(mask: typing.List[typing.List[int]]) -> bytes:
        return zlib.compress(json.dumps(mask).encode('utf-8'))

    @staticmethod
    def _decompress_mask(mask_bytes: bytes) -> typing.List[typing.List[int]]:
        return json.loads(zlib.decompress(mask_bytes).decode('utf-8'))

    @staticmethod
    def _to_model(hold: hold_schema.HoldSchema) -> holds.HoldModel:
        return holds.HoldModel(
            id=str(hold.id),
            bbox=hold.bbox,
            mask=HoldDAO._decompress_mask(hold.mask) if hold.mask else []
        )

    @staticmethod
    @base_dao.with_session
    def get_all_holds(session: sqlalchemy.orm.Session) -> typing.List[holds.HoldModel]:
        hold_records = session.query(hold_schema.HoldSchema).all()
        return [HoldDAO._to_model(hold) for hold in hold_records]

    @staticmethod
    @base_dao.with_session
    def get_hold_by_id(hold_id: int, session: sqlalchemy.orm.Session) -> holds.HoldModel:
        hold = session.query(hold_schema.HoldSchema).get(hold_id)
        if hold is None:
            raise ValueError("Hold with given ID does not exist.")
        return HoldDAO._to_model(hold)

    @staticmethod
    @base_dao.with_session
    def get_holds_by_ids(
        hold_ids: typing.List[int],
        session: sqlalchemy.orm.Session
    ) -> typing.List[holds.HoldModel]:
        hold_records = session.query(hold_schema.HoldSchema) \
            .filter(hold_schema.HoldSchema.id.in_(hold_ids)) \
            .all()
        return [HoldDAO._to_model(hold) for hold in hold_records]

    @staticmethod
    @base_dao.with_session
    def save_hold(hold_model: holds.HoldModel, session: sqlalchemy.orm.Session):
        hold = hold_schema.HoldSchema(
            bbox=hold_model.bbox,
            mask=HoldDAO._compress_mask(hold_model.mask) if hold_model.mask else None,
        )
        session.add(hold)
        session.flush()
        hold_model.id = str(hold.id)