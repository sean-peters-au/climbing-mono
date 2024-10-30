import os

class Config:
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGODB_HOST'),
        'db': os.environ.get('MONGODB_DB'),
    }

    S3 = {
        'AWS_ACCESS_KEY_ID': os.environ.get('S3_AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.environ.get('S3_AWS_SECRET_ACCESS_KEY'),
        'BUCKET': os.environ.get('S3_BUCKET'),
    }

    IMAGE_PROCESSING = {
        'url': os.environ.get('IMAGE_PROCESSING_HOST'),
    }

    POSTGRES = {
        'URI': os.environ.get('POSTGRES_URI'),
    }
