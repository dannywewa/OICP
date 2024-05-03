import numpy as np

def flatfieldcorrect(raw_image: np.ndarray, dark_field_img: np.ndarray, bright_field_img: np.ndarray) -> np.ndarray:
    """
    https://en.wikipedia.org/wiki/Flat-field_correction

    C=(R-D)/(F-D)*(avg of high)
    """
    result = (raw_image - dark_field_img)/bright_field_img
    return result

