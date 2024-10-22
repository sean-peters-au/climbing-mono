import db.schema
import business.models.routes
import business.models.recordings

def get_route(route_id):
    route_db = db.schema.Route.objects.get(id=route_id)
    return business.models.routes.RouteModel.from_mongo(route_db)

def get_route_recordings(route_id):
    # Use the route_id to query the recordings
    recordings_db = db.schema.Recording.objects(route=route_id)

    recordings = [
        business.models.recordings.RecordingModel.from_mongo(recording)
        for recording in recordings_db
    ]

    return recordings
