import numpy as np
import cv2
import PIL

def pil_to_cv(image):
    """
    Convert a PIL image to a CV image.
    """
    image = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image

def cv_to_pil(image):
    """
    Convert a CV image to a PIL image.
    """

    return PIL.Image.fromarray(image)