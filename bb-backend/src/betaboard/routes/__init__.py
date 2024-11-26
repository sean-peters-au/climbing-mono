import betaboard.routes.wall as wall_routes
import betaboard.routes.route as route_routes
import betaboard.routes.sensor as sensor_routes
import betaboard.routes.recording as recording_routes

blueprints = [
    recording_routes.recording_bp,
    wall_routes.wall_bp,
    route_routes.routes_bp,
    sensor_routes.sensor_bp,
]
