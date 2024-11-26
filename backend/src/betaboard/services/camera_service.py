import requests

from betaboard.services import service

class CameraClient(service.Service):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.url = app.config['CAMERA_SERVICE']['url']
        app.extensions['camera_service'] = self

    def start_recording(self) -> bool:
        """
        Start recording video on the camera service.

        Returns:
            bool: True if recording started successfully.

        Raises:
            requests.RequestException: If the camera service request fails.
        """
        response = requests.post(f"{self.url}/start_recording")
        response.raise_for_status()
        return response.status_code == 200

    def stop_recording(self) -> bytes:
        """
        Stop recording video on the camera service and retrieve the recorded video.

        Returns:
            bytes: The recorded video data.

        Raises:
            requests.RequestException: If the camera service request fails.
        """
        response = requests.post(f"{self.url}/stop_recording")
        response.raise_for_status()
        return response.content