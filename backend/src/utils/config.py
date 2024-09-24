import os

class Config:
    MONGODB_SETTINGS = {
        'host': 'mongodb://mongo:27017',
        'db': os.environ.get('MONGODB_DB', 'climbing'),
    }

    SEGMENT_ANYTHING = {
        # 'checkpoint_path': './static/sam_vit_h_4b8939.pth',
        # 'model_type': 'vit_h',
        'checkpoint_path': '../static/sam_vit_l_0b3195.pth',
        'model_type': 'vit_l',
        'min_hold_size': 10,
        'max_hold_size': 150000,
        'new_image_affine_match_threshold': 50,
    }

    S3 = {
        'AWS_ACCESS_KEY_ID': 'AKIA3FLD3PDHZC7FYYOF',
        'AWS_SECRET_ACCESS_KEY': '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',
        'BUCKET': 'woody-climbing-dev',
    }
