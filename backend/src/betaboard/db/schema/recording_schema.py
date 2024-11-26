import sqlalchemy
import sqlalchemy.orm

import betaboard.db.schema.base_schema as base_schema


class SensorReadingSchema(base_schema.BaseSchema):
    __tablename__ = 'sensor_readings'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    recording_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('recordings.id'))
    hold_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('holds.id'))
    frame_index = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    x = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    y = sqlalchemy.Column(sqlalchemy.Float, nullable=False)

    # Relationships
    recording = sqlalchemy.orm.relationship('RecordingSchema', back_populates='sensor_readings')
    hold = sqlalchemy.orm.relationship('HoldSchema')


class RecordingSchema(base_schema.BaseSchema):
    __tablename__ = 'recordings'

    route_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('routes.id'), nullable=False)
    start_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    end_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    video_s3_key = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(
        sqlalchemy.Enum('recording', 'completed', 'failed', name='recording_status'),
        nullable=False,
        default='recording'
    )

    # Relationships
    route = sqlalchemy.orm.relationship('RouteSchema', back_populates='recordings')
    sensor_readings = sqlalchemy.orm.relationship('SensorReadingSchema', back_populates='recording')
