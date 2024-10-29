import typing
import db.schema
import business.models.recordings
import mongoengine.errors

class RecordingDAO:
    @staticmethod
    def get_all_recordings() -> typing.List[business.models.recordings.RecordingModel]:
        recordings = db.schema.Recording.objects().all()
        return [business.models.recordings.RecordingModel.from_mongo(recording) for recording in recordings]

    @staticmethod
    def get_recording_by_id(recording_id: str) -> business.models.recordings.RecordingModel:
        try:
            recording = db.schema.Recording.objects.get(id=recording_id)
        except mongoengine.errors.DoesNotExist:
            raise ValueError("Recording with given ID does not exist.")
        return business.models.recordings.RecordingModel.from_mongo(recording)

    @staticmethod
    def get_recordings_by_ids(recording_ids: typing.List[str]) -> typing.List[business.models.recordings.RecordingModel]:
        recordings = db.schema.Recording.objects(id__in=recording_ids)
        return [business.models.recordings.RecordingModel.from_mongo(recording) for recording in recordings]

    @staticmethod
    def get_recordings_by_route_id(route_id: str) -> typing.List[business.models.recordings.RecordingModel]:
        recordings = db.schema.Recording.objects(route=route_id)
        return [business.models.recordings.RecordingModel.from_mongo(recording) for recording in recordings]

    @staticmethod
    def save_recording(recording_model: business.models.recordings.RecordingModel):
        sensor_readings_frames_db = [
            [
                db.schema.SensorReading(
                    hold=reading.hold_id,
                    x=reading.x,
                    y=reading.y,
                )
                for reading in frame
            ]
            for frame in recording_model.sensor_readings
        ]

        recording_schema = db.schema.Recording(
            route=recording_model.route_id,
            start_time=recording_model.start_time,
            end_time=recording_model.end_time,
            sensor_readings=sensor_readings_frames_db,
        )
        recording_schema.save()
        recording_model.id = str(recording_schema.id)