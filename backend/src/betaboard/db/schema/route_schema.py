import sqlalchemy
import sqlalchemy.orm

import betaboard.db.schema.base_schema as base_schema


route_holds = sqlalchemy.Table(
    'route_holds',
    base_schema.BaseSchema.metadata,
    sqlalchemy.Column('route_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('routes.id')),
    sqlalchemy.Column('hold_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('holds.id'))
)

class RouteSchema(base_schema.BaseSchema):
    __tablename__ = 'routes'

    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    grade = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.DateTime)
    wall_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('walls.id'))

    # Relationships
    wall = sqlalchemy.orm.relationship('WallSchema', back_populates='routes')
    holds = sqlalchemy.orm.relationship('HoldSchema', secondary=route_holds, back_populates='routes')
    recordings = sqlalchemy.orm.relationship('RecordingSchema', back_populates='route')
