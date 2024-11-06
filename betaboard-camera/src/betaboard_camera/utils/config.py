import os

class Config:
    VIDEO_SEGMENT_DURATION = int(os.environ.get('VIDEO_SEGMENT_DURATION'))
    VIDEO_SEGMENT_NUMBER = int(os.environ.get('VIDEO_SEGMENT_NUMBER'))
    VIDEO_DIR = os.environ.get('VIDEO_DIR')
