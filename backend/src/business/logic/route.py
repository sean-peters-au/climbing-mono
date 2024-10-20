import db.schema
import business.models.recordings

def get_route_recordings(route_id):
    # Use the route_id to query the recordings
    recordings_db = db.schema.Recording.objects(route=route_id)

    recordings = [
        business.models.recordings.RecordingModel.from_mongo(recording)
        for recording in recordings_db
    ]

    return recordings
