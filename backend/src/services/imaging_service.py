import requests

from . import service

class ImageProcessingClient(service.Service):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.url = app.config['IMAGE_PROCESSING']['url'] + '/api/'
        app.extensions['image_processing'] = self

    def _make_request(self, endpoint, data):
        print(f"{self.url}{endpoint}")
        response = requests.post(f"{self.url}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()

    def auto_segment(self, image):
        return self._make_request(
            '/board/auto_segment',
            {
                'image': image,
            },
        )

    def segment_hold(self, image, x, y):
        return self._make_request(
            '/board/segment_hold',
            {
                'image': image,
                'x': x,
                'y': y,
            },
        )

    def transform_board(self, image, board=None, kickboard=None, mask=False, flatten=False):
        return self._make_request(
            '/board/transform',
            {
                'image': image,
                'board': board,
                'kickboard': kickboard,
                'mask': mask,
                'flatten': flatten
            }
        )