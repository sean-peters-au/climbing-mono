import numpy as np
import cv2

import business.logic.utils as utils

def transform_board(image, board, kickboard, mask, flatten):
    """
    Transform an image of a climbing board.
    """
    pass

def get_perspective_image(image, wall_annotations, cv_image=False):
    """
    Get a perspective image of the climbing wall from the original image.

    Args:
        image (PIL.Image.Image): The original image.
        wall_annotations (list): A list of (x, y) tuples representing the polygon of the wall.

    Returns:
        MatLike: The perspective image.
    """
    if not cv_image:
        cv_image = utils.pil_to_cv(image)
    else:
        cv_image = image

    # Coordinates provided for the four corners of the climbing wall
    # Format: (x, y)
    top_left = (wall_annotations[0]['x'], wall_annotations[0]['y'])
    top_right = (wall_annotations[1]['x'], wall_annotations[1]['y'])
    bottom_right = (wall_annotations[2]['x'], wall_annotations[2]['y'])
    bottom_left = (wall_annotations[3]['x'], wall_annotations[3]['y'])

    print('top_left', top_left)
    print('top_right', top_right)
    print('bottom_left', bottom_left)
    print('bottom_right', bottom_right)

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
        cv_image = utils.pil_to_cv(image)
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