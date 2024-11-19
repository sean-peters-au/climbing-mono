import typing
import sqlalchemy.orm

import betaboard.db.schema.recording_schema as recording_schema
import betaboard.business.models.recordings as recordings_model
import betaboard.db.dao.base_dao as base_dao

class RecordingDAO:
    @staticmethod
    def _to_model(recording: recording_schema.RecordingSchema) -> recordings_model.RecordingModel:
        sensor_readings = []
        # Group sensor readings by frame index
        readings_by_frame = {}
        for reading in recording.sensor_readings:
            frame_index = reading.frame_index
            if frame_index not in readings_by_frame:
                readings_by_frame[frame_index] = []
            readings_by_frame[frame_index].append(
                recordings_model.SensorReadingModel(
                    hold_id=str(reading.hold_id),
                    x=reading.x,
                    y=reading.y,
                )
            )
        # Sort frames by index
        for frame_index in sorted(readings_by_frame.keys()):
            sensor_readings.append(readings_by_frame[frame_index])

        return recordings_model.RecordingModel(
            id=str(recording.id),
            route_id=recording.route_id,
            start_time=recording.start_time,
            end_time=recording.end_time,
            sensor_readings=sensor_readings,
            video_s3_key=recording.video_s3_key
        )

    @staticmethod
    @base_dao.with_session
    def get_all_recordings(session: sqlalchemy.orm.Session) -> typing.List[recordings_model.RecordingModel]:
        recording_records = session.query(recording_schema.RecordingSchema).all()
        return [RecordingDAO._to_model(rec) for rec in recording_records]

    @staticmethod
    @base_dao.with_session
    def get_recording_by_id(recording_id: int, session: sqlalchemy.orm.Session) -> recordings_model.RecordingModel:
        recording = session.query(recording_schema.RecordingSchema).get(recording_id)
        if recording is None:
            raise ValueError("Recording with given ID does not exist.")
        return RecordingDAO._to_model(recording)

    @staticmethod
    @base_dao.with_session
    def get_recordings_by_ids(
        recording_ids: typing.List[int],
        session: sqlalchemy.orm.Session
    ) -> typing.List[recordings_model.RecordingModel]:
        recording_records = session.query(recording_schema.RecordingSchema)\
            .filter(recording_schema.RecordingSchema.id.in_(recording_ids))\
            .all()
        return [RecordingDAO._to_model(rec) for rec in recording_records]

    @staticmethod
    @base_dao.with_session
    def get_recordings_by_route_id(
        route_id: int,
        session: sqlalchemy.orm.Session
    ) -> typing.List[recordings_model.RecordingModel]:
        recording_records = session.query(recording_schema.RecordingSchema)\
            .filter(recording_schema.RecordingSchema.route_id == route_id)\
            .all()
        return [RecordingDAO._to_model(rec) for rec in recording_records]

    @staticmethod
    @base_dao.with_session
    def save_recording(recording_model: recordings_model.RecordingModel, session: sqlalchemy.orm.Session):
        recording = recording_schema.RecordingSchema(
            route_id=recording_model.route_id,
            start_time=recording_model.start_time,
            end_time=recording_model.end_time,
            video_s3_key=recording_model.video_s3_key,
        )
        session.add(recording)
        session.flush()  # Get the recording ID

        # Create sensor readings
        for frame_idx, frame in enumerate(recording_model.sensor_readings):
            for reading in frame:
                sensor_reading = recording_schema.SensorReadingSchema(
                    recording_id=recording.id,
                    hold_id=reading.hold_id,
                    frame_index=frame_idx,
                    x=float(reading.x),
                    y=float(reading.y),
                )
                session.add(sensor_reading)

        session.flush()
        recording_model.id = str(recording.id)