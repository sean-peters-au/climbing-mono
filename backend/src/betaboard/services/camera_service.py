import requests

from betaboard.services import service

class CameraClient(service.Service):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.url = app.config['CAMERA_SERVICE']['url']
        app.extensions['camera_service'] = self

    def get_video(self, start: int, end: int) -> bytes:
        """
        Fetches video data from the camera service between start and end times.

        :param start: Start timestamp in seconds.
        :param end: End timestamp in seconds.
        :return: Bytes of the video file.
        """
        params = {'start': start, 'end': end}
        response = requests.get(f"{self.url}/video", params=params)
        response.raise_for_status()
        return response.content