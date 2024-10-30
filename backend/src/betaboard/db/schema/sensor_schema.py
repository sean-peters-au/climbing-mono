import sqlalchemy
import sqlalchemy.orm

import betaboard.db.schema.base_schema as base_schema


class SensorSchema(base_schema.BaseSchema):
    __tablename__ = 'sensors'

    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    ip_address = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    hold_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('holds.id'))
