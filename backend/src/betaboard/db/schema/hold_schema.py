import sqlalchemy
import sqlalchemy.orm

import betaboard.db.schema.base_schema as base_schema


class HoldSchema(base_schema.BaseSchema):
    __tablename__ = 'holds'

    bbox = sqlalchemy.Column(sqlalchemy.JSON)
    mask = sqlalchemy.Column(sqlalchemy.LargeBinary)

    # Relationships
    wall_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('walls.id'))
    wall = sqlalchemy.orm.relationship('WallSchema', back_populates='holds')
    routes = sqlalchemy.orm.relationship('RouteSchema', secondary='route_holds', back_populates='holds')
