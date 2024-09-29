import uuid
import boto3

from . import service

class S3Client(service.Service):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.client = boto3.client(
            's3',
            aws_access_key_id=app.config['S3']['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['S3']['AWS_SECRET_ACCESS_KEY'],
        )
        self.bucket = app.config['S3']['BUCKET']
        app.extensions['s3'] = self

    def _generate_file_key(self):
        return str(uuid.uuid4())

    def upload_file(self, file):
        object_name = self._generate_file_key()
        file.seek(0)  # Ensure the file's read-pointer is at the start
        self.client.upload_fileobj(file, self.bucket, object_name)

        return object_name

    def get_file_url(self, uuid):
        return self.client.generate_presigned_url('get_object', Params={'Bucket': self.bucket, 'Key': uuid})

    def get_file(self, uuid):
        try:
            file_object = self.client.get_object(Bucket=self.bucket, Key=uuid)
            return file_object['Body']
        except self.client.exceptions.NoSuchKey:
            print('No such key: ', uuid)
            return None

    def delete_file(self, uuid):
        response = self.client.delete_object(Bucket=self.bucket, Key=uuid)
        return uuid
