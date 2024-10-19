import dataclasses

import requests

from . import service

@dataclasses.dataclass
class Segment:
    bbox: list
    mask: list

    def asdict(self):
        return dataclasses.asdict(self)

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

    def auto_segment(self, image_url: str) -> list[Segment]:
        response = self._make_request(
            '/board/auto_segment',
            {
                'image_url': image_url,
            },
        )
        segments = [
            Segment(
                bbox=segment['bbox'],
                mask=segment['mask'],
            )
            for segment in response['segments']
        ]
        return segments

    def segment_hold(self, image_url: str, x: int, y: int) -> Segment:
        response = self._make_request(
            '/board/segment_hold',
            {
                'image_url': image_url,
                'x': x,
                'y': y,
            },
        )
        return Segment(
            bbox=response['bbox'],
            mask=response['mask'],
        )

    def transform_board(self, image_url: str, board: dict=None, kickboard: dict=None, mask: bool=False, flatten: bool=False) -> str:
        response = self._make_request(
            '/board/transform',
            {
                'image_url': image_url,
                'board': board,
                'kickboard': kickboard,
                'mask': mask,
                'flatten': flatten
            }
        )
        return response['image_url']