import collections

import flask
import lang_sam
import numpy as np
import segment_anything

import business.logic.utils as utils

Segment = collections.namedtuple('Segment', ['mask', 'bbox'])

def segment_holds_from_image(image, cv_image=False):
    """
    Segment holds from an image.

    Args:
        image (PIL.Image.Image): The image to segment.
        cv_image (bool): Whether the image is a CV image.

    Returns:
        list: A list of holds.
    """
    if not cv_image:
        cv_image = utils.pil_to_cv(image)
    else:
        cv_image = image

    # Convert the CV image to a PIL image
    image_pil = utils.cv_to_pil(cv_image)

    model_name = flask.current_app.config['SEGMENT_ANYTHING']['model_type']
    checkpoint_path = flask.current_app.config['SEGMENT_ANYTHING']['checkpoint_path']

    model = lang_sam.LangSAM(model_name, checkpoint_path)
    
    text_prompt = "object"
    masks, _, _, _ = model.predict(image_pil, text_prompt, 0.03, 0.03)

    # Assuming masks is a tensor, convert it to a numpy array
    masks = masks.cpu().numpy()

    # Filter out masks that are too big or too small to be climbing holds
    filtered_masks = [
        mask for mask in masks
        if flask.current_app.config['SEGMENT_ANYTHING']['min_hold_size'] < mask.sum() < flask.current_app.config['SEGMENT_ANYTHING']['max_hold_size']
    ]

    # Clip masks to their bounding box
    holds = []
    for mask in filtered_masks:
        y_indices, x_indices = mask.nonzero()
        x_min, x_max = x_indices.min(), x_indices.max()
        y_min, y_max = y_indices.min(), y_indices.max()
        bbox = [x_min, y_min, x_max - x_min, y_max - y_min]
        segmentation = mask[y_min:y_max+1, x_min:x_max+1]
        holds.append(Segment(mask=segmentation.tolist(), bbox=bbox))

    return holds

def segment_hold_from_image(image, x, y, cv_image=False):
    """
    Segment a hold from an image.

    Args:
        image (PIL.Image.Image): The image to segment.
        cv_image (bool): Whether the image is a CV image.
        x (int): The x coordinate of the hold to segment.
        y (int): The y coordinate of the hold to segment.
    """
    if not cv_image:
        cv_image = utils.pil_to_cv(image)
    else:
        cv_image = image

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

    mask = masks[0]
    
    # Get the bounding box of the hold
    y_indices, x_indices = mask.nonzero()
    x_min, x_max = x_indices.min(), x_indices.max()
    y_min, y_max = y_indices.min(), y_indices.max()
    bbox = [x_min, y_min, x_max - x_min, y_max - y_min]

    return Segment(mask=mask.tolist(), bbox=bbox)