import os

class Config:
    SEGMENT_ANYTHING = {
        'checkpoint_path': os.environ.get('SEGMENT_ANYTHING_CHECKPOINT_PATH'),
        'model_type': os.environ.get('SEGMENT_ANYTHING_MODEL_TYPE'),
        'min_hold_size': float(os.environ.get('SEGMENT_ANYTHING_MIN_HOLD_SIZE')),
        'max_hold_size': float(os.environ.get('SEGMENT_ANYTHING_MAX_HOLD_SIZE')),
        'new_image_affine_match_threshold': float(os.environ.get('SEGMENT_ANYTHING_NEW_IMAGE_AFFINE_MATCH_THRESHOLD')),
    }

print(f'Config: {Config.SEGMENT_ANYTHING}')