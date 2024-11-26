import io

import flask
import cv2
import lang_sam
import numpy as np
import segment_anything
import PIL

import business.logic.utils as utils
import utils.logging

import dataclasses

@dataclasses.dataclass
class Segment:
    mask: list
    bbox: list

    def asdict(self):
        return dataclasses.asdict(self)

def segment_holds_from_image(image_bytes):
    """
    Segment holds from an image.

    Args:
        image (bytes): The image to segment.

    Returns:
        list: A list of holds.
    """
    print(f'image_bytes')
    image = PIL.Image.open(io.BytesIO(image_bytes))

    if image.mode == 'RGBA':
        image = image.convert('RGB')

    model_name = flask.current_app.config['SEGMENT_ANYTHING']['model_type']
    checkpoint_path = flask.current_app.config['SEGMENT_ANYTHING']['checkpoint_path']

    model = lang_sam.LangSAM(model_name, checkpoint_path)

    text_prompt = "object"
    masks, _, _, _ = model.predict(image, text_prompt, 0.05, 0.05)

    # Assuming masks is a tensor, convert it to a numpy array
    masks = masks.cpu().numpy()

    min_hold_size_percent = flask.current_app.config['SEGMENT_ANYTHING']['min_hold_size']
    max_hold_size_percent = flask.current_app.config['SEGMENT_ANYTHING']['max_hold_size']

    # Filter out masks that are too big or too small to be climbing holds
    # The is basically guessed by configured percentages
    total_pixels = image.size[0] * image.size[1]
    filtered_masks = [
        mask for mask in masks
        if min_hold_size_percent < (mask.sum() / total_pixels) < max_hold_size_percent
    ]

    # Clip masks to their bounding box
    segments = [
        _mask_to_segment(mask)
        for mask in filtered_masks
    ]

    return segments

def segment_hold_from_image(image_bytes, x, y):
    """
    Segment a hold from an image.

    Args:
        image (bytes): The image to segment.
        cv_image (bool): Whether the image is a CV image.
        x (int): The x coordinate of the hold to segment.
        y (int): The y coordinate of the hold to segment.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    utils.logging.logger().info(f'image shape: {image.shape}')

    model_name = flask.current_app.config['SEGMENT_ANYTHING']['model_type']
    checkpoint_path = flask.current_app.config['SEGMENT_ANYTHING']['checkpoint_path']

    # Load the SAM model
    sam = segment_anything.sam_model_registry[model_name](checkpoint_path)
    predictor = segment_anything.SamPredictor(sam)

    # Set the image for prediction
    predictor.set_image(image)

    # Prepare the point and label (1 for foreground)
    input_point = np.array([[x, y]])
    input_label = np.array([1])

    # Perform prediction with the point prompt
    masks, _, _ = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=False
    )

    # Filter out masks that are too big or too small to be climbing holds
    utils.logging.logger().info(f'masks: {masks}')
    filtered_masks = [
        mask for mask in masks
        if flask.current_app.config['SEGMENT_ANYTHING']['min_hold_size'] < mask.sum() < flask.current_app.config['SEGMENT_ANYTHING']['max_hold_size']
    ]

    mask = filtered_masks[0]
    utils.logging.logger().info(f'mask shape: {mask.shape}')
    
    return _mask_to_segment(mask)

def _mask_to_segment(mask: np.ndarray) -> Segment:
    """
    Convert a mask to a segment.
    """
    mask = mask.astype(int)
 
    y_indices, x_indices = mask.nonzero()
    x_min, x_max = int(x_indices.min()), int(x_indices.max())
    y_min, y_max = int(y_indices.min()), int(y_indices.max())

    segment_bbox = [x_min, y_min, x_max - x_min, y_max - y_min]

    segment_mask = mask[y_min:y_max+1, x_min:x_max+1]
    segment_mask = segment_mask.tolist()

    return Segment(mask=segment_mask, bbox=segment_bbox)