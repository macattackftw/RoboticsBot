from __future__ import division, print_function

import cv2
import numpy as np
from std_msgs.msg import String

from robot.common import POI

from .camera_base import Camera
from .mask import mask_image


class StoplightCamera(Camera):
    """Camera class for stoplight detection."""

    # The portion of the image we focus on. (y-slice, x-slice).
    REGION_OF_INTEREST = (slice(470, 480, None), slice(0, None, None))
    # How much do we blur the image
    BLUR_KERNEL = (5, 5)
    SENSITIVITY = 50
    # How many red pixels count as a stoplight. Lol.
    STOP_THRESHOLD = 1000

    def process_image(self, hsv_image):
        """ Publish a notification of a stoplight is encountered.
            inspiration: https://stackoverflow.com/a/25401596
        """
        # Crop the image to deal only with whatever is directly in front of us.
        hsv_image = hsv_image[self.REGION_OF_INTEREST]

        white_mask = mask_image(hsv_image, (0, 0, 255 - self.SENSITIVITY),
                                (255, self.SENSITIVITY, 255))
        black_mask = mask_image(hsv_image, (0, 0, 0), (180, 255, 200))

        if self.verbose:
            cv2.namedWindow('Stoplight W Mask', cv2.WINDOW_NORMAL)
            cv2.imshow('Stoplight W Mask', white_mask)

            cv2.namedWindow('Stoplight BLK Mask', cv2.WINDOW_NORMAL)
            cv2.imshow('Stoplight BLK Mask', black_mask)

        # Join the two masks.
        mask = white_mask + black_mask
        # Swap 0 and 255 values...
        mask[mask == 0] = 1
        mask[mask >= 255] = 0
        mask[mask == 1] = 255

        # We see a stoplight if there are more than some number of red pixels.
        if np.sum(mask) / 255 > self.STOP_THRESHOLD:
            msg = String()
            msg.data = POI['STOPLIGHT']
            self.publisher.publish(msg)

        if self.verbose:
            # Mask out only the reds. Everything else will be black.
            # masked = cv2.bitwise_and(cropped, cropped, mask=mask)
            cv2.namedWindow('Stoplight W+B Mask', cv2.WINDOW_NORMAL)
            cv2.imshow('Stoplight W+B Mask', mask)
