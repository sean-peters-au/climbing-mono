import flask
import numpy as np
import cv2
import PIL
import lang_sam

def _to_cv_image(image):
    # Read the image file using cv2
    image = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
    # Convert the image to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image

def _to_pil_image(image):
    # Convert the CV image to a PIL image
    return PIL.Image.fromarray(image)

def segment_holds_from_image(image, cv_image=False):
    if not cv_image:
        cv_image = _to_cv_image(image)
    else:
        cv_image = image

    # Convert the CV image to a PIL image
    image_pil = _to_pil_image(cv_image)

    model = lang_sam.LangSAM(flask.current_app.config['SEGMENT_ANYTHING']['model_type'], flask.current_app.config['SEGMENT_ANYTHING']['checkpoint_path'])
    
    text_prompt = "object"
    masks, boxes, phrases, logits = model.predict(image_pil, text_prompt, 0.03, 0.03)

    # Assuming masks is a tensor, convert it to a numpy array
    masks = masks.cpu().numpy()

    print('masks', len(masks))
    print('boxes', len(boxes))
    print('phrases', len(phrases))
    print('logits', len(logits))

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
        holds.append({
            'bbox': bbox,
            'mask': segmentation.tolist(),
        })

    return holds

def get_perspective_image(image, wall_annotations, cv_image=False):
    if not cv_image:
        cv_image = _to_cv_image(image)
    else:
        cv_image = image

    # Coordinates provided for the four corners of the climbing wall
    # Format: (x, y)
    top_left = (wall_annotations[0]['x'], wall_annotations[0]['y'])
    top_right = (wall_annotations[1]['x'], wall_annotations[1]['y'])
    bottom_right = (wall_annotations[2]['x'], wall_annotations[2]['y'])
    bottom_left = (wall_annotations[3]['x'], wall_annotations[3]['y'])

    # Corresponding points in the output image
    # We will choose the width and height based on the furthest points
    output_width = max(top_right[0] - top_left[0], bottom_right[0] - bottom_left[0])
    output_height = max(bottom_left[1] - top_left[1], bottom_right[1] - top_right[1])

    # Destination points need to form a rectangle for the affine transformation
    dst_points = np.array([
        [0, 0],
        [output_width - 1, 0],
        [0, output_height - 1],
        [output_width - 1, output_height - 1]
    ], dtype='float32')

    # Source points from the input image
    src_points = np.array([
        top_left,
        top_right,
        bottom_left,
        bottom_right
    ], dtype='float32')

    print('dst_points', dst_points)
    print('src_points', src_points)
    print('output_width', output_width)
    print('output_height', output_height)

    # Compute the perspective transform matrix and then apply it
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    perspective_image = cv2.warpPerspective(cv_image, matrix, (int(output_width), int(output_height)))

    # Convert the image back to RGB
    perspective_image = cv2.cvtColor(perspective_image, cv2.COLOR_BGR2RGB)

    return perspective_image

def get_cropped_image(image, wall_annotations, cv_image=False):
    """
    Get a cropped image of the climbing wall from the original image.

    Args:
        image (PIL.Image.Image): The original image.
        wall_annotations (list): A list of (x, y) tuples representing the polygon of the wall.

    Returns:
        MatLike: The cropped image.
    """
    if not cv_image:
        cv_image = _to_cv_image(image)
    else:
        cv_image = image

    # Convert the polygon to a numpy array
    polygon = np.array([wall_annotations], dtype=np.int32)

    # Create a mask for the polygon
    mask = np.zeros((cv_image.shape[0], cv_image.shape[1]), dtype=np.uint8)
    cv2.fillPoly(mask, polygon, 255)

    # Apply the mask to the image
    cropped_image = cv2.bitwise_and(cv_image, cv_image, mask=mask)
    # Convert the image back to RGB
    cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)

    return cropped_image