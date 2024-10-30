import sqlalchemy
import sqlalchemy.orm

import betaboard.db.schema.base_schema as base_schema


class WallSchema(base_schema.BaseSchema):
    __tablename__ = 'walls'

    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    height = sqlalchemy.Column(sqlalchemy.Integer)
    width = sqlalchemy.Column(sqlalchemy.Integer)
    image_id = sqlalchemy.Column(sqlalchemy.String)

    # Relationships
    holds = sqlalchemy.orm.relationship('HoldSchema', back_populates='wall')
    routes = sqlalchemy.orm.relationship('RouteSchema', back_populates='wall')
