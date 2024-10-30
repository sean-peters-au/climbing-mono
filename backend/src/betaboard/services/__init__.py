from betaboard.services import s3
from betaboard.services import imaging_service

def init_services(app):
    services = (
        s3.S3Client(),
        imaging_service.ImageProcessingClient(),
    )

    for service in services:

        service.init_app(app)