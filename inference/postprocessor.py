import cv2
import numpy as np


def erosion(img, itr=1, bilateral_filter=True):
    img_rgb, img_alpha = img[:, :, :-1], np.expand_dims(img[:, :, -1], axis=-1)

    if bilateral_filter:
        img_rgb = cv2.bilateralFilter(img_rgb, 7, 64, 64)

    # erosion
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    img_erosion = cv2.erode(img_rgb, k, iterations=itr)

    if bilateral_filter:
        img_erosion = cv2.bilateralFilter(img_erosion, 16, 64, 64)
    img_result = np.concatenate([img_erosion, img_alpha], axis=-1)

    return img_result

