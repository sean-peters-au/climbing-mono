import datetime
import typing
import sqlalchemy.orm

import betaboard.db.schema.recording_schema as recording_schema
import betaboard.business.models.recordings as recordings_model
import betaboard.db.dao.base_dao as base_dao

class RecordingDAO:
    @staticmethod
    def _to_model(recording: recording_schema.RecordingSchema) -> recordings_model.RecordingModel:
        """
        Convert a recording schema to a recording model.

        Args:
            recording: The recording schema to convert.

        Returns:
            RecordingModel: The converted recording model.
        """
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
            route_id=str(recording.route_id),
            start_time=recording.start_time,
            end_time=recording.end_time,
            sensor_readings=sensor_readings,
            video_s3_key=recording.video_s3_key,
            status=recording.status
        )

    @staticmethod
    @base_dao.with_session
    def create_recording(
        route_id: str,
        start_time: datetime.datetime,
        session: sqlalchemy.orm.Session
    ) -> recordings_model.RecordingModel:
        """
        Create a new recording.

        Args:
            route_id: ID of the route being recorded.
            start_time: Start time of the recording.
            session: Database session.

        Returns:
            RecordingModel: The created recording model.
        """
        recording = recording_schema.RecordingSchema(
            route_id=route_id,
            start_time=start_time,
            status='recording'
        )
        session.add(recording)
        session.flush()
        return RecordingDAO._to_model(recording)

    @staticmethod
    @base_dao.with_session
    def update_recording(
        recording_id: str,
        end_time: typing.Optional[datetime.datetime] = None,
        video_s3_key: typing.Optional[str] = None,
        status: typing.Optional[str] = None,
        sensor_readings: typing.Optional[typing.List[typing.List[recordings_model.SensorReadingModel]]] = None,
        session: sqlalchemy.orm.Session = None
    ) -> recordings_model.RecordingModel:
        """
        Update a recording's details.

        Args:
            recording_id (str): ID of the recording to update.
            end_time (Optional[datetime.datetime]): Optional end time of the recording.
            video_s3_key (Optional[str]): Optional S3 key for the video.
            status (Optional[str]): Optional new status for the recording.
            sensor_readings (Optional[List[List[SensorReadingModel]]]): Optional list of sensor reading frames.
            session (Session): Database session.

        Returns:
            RecordingModel: The updated recording model.

        Raises:
            ValueError: If recording not found.
        """
        recording = session.query(recording_schema.RecordingSchema).get(recording_id)
        if recording is None:
            raise ValueError("Recording not found")

        if end_time is not None:
            recording.end_time = end_time
        if video_s3_key is not None:
            recording.video_s3_key = video_s3_key
        if status is not None:
            recording.status = status
        if sensor_readings is not None:
            # Create sensor readings
            for frame_idx, frame in enumerate(sensor_readings):
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
        return RecordingDAO._to_model(recording)

    @staticmethod
    @base_dao.with_session
    def get_recording_by_id(
        recording_id: str,
        session: sqlalchemy.orm.Session
    ) -> recordings_model.RecordingModel:
        """
        Get a recording by its ID.

        Args:
            recording_id: ID of the recording to retrieve.
            session: Database session.

        Returns:
            RecordingModel: The requested recording model.

        Raises:
            ValueError: If recording not found.
        """
        recording = session.query(recording_schema.RecordingSchema).get(recording_id)
        if recording is None:
            raise ValueError("Recording not found")
        return RecordingDAO._to_model(recording)

    @staticmethod
    @base_dao.with_session
    def get_all_recordings(session: sqlalchemy.orm.Session) -> typing.List[recordings_model.RecordingModel]:
        recording_records = session.query(recording_schema.RecordingSchema).all()
        return [RecordingDAO._to_model(rec) for rec in recording_records]

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