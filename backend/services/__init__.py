from . import s3

def init_services(app):
    services = (
        s3.S3Client(),
    )

    for service in services:
        service.init_app(app)