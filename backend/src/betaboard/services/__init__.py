from betaboard.services import s3
from betaboard.services import imaging_service
from betaboard.services import camera_service

def init_services(app):
    services = (
        s3.S3Client(),
        imaging_service.ImageProcessingClient(),
        camera_service.CameraClient(),
    )

    for service_instance in services:
        service_instance.init_app(app)