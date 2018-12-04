from __future__ import division, print_function

import cv2
import numpy as np
from std_msgs.msg import String

from robot.common import STOPLIGHT

from .camera_base import Camera


class StoplightCamera(Camera):
    """Camera class for stoplight detection."""

    # The portion of the image we focus on. (y-slice, x-slice).
    REGION_OF_INTEREST = (slice(470, 480, None), slice(0, None, None))
    # How much do we blur the image
    BLUR_KERNEL = (5, 5)
    # How many red pixels count as a stoplight. Lol.
    RED_SENSITIVITY = 500

    def process_image(self, hsv_image):
        """Publish a notification of a stoplight is encountered."""
        # Crop the image to deal only with whatever is directly in front of us.
        cropped = hsv_image[self.REGION_OF_INTEREST]
        # Blur the image before doing anything.
        blurred = cv2.GaussianBlur(cropped, self.BLUR_KERNEL, 0)

        # In the HSV color space, red ranges from 0-10 and from 170-180, so
        # we need two masks.

        red_low_low = np.array([0, 50, 50])
        red_low_high = np.array([10, 255, 255])

        red_high_low = np.array([160, 50, 50])
        red_high_high = np.array([180, 255, 255])

        lower_mask = cv2.inRange(blurred, red_low_low, red_low_high)
        upper_mask = cv2.inRange(blurred, red_high_low, red_high_high)

        # Join the two masks.
        mask = lower_mask + upper_mask
        # We see a stoplight if there are more than some number of red pixels.
        if np.sum(mask) / 255 > self.RED_SENSITIVITY:
            msg = String()
            msg.data = STOPLIGHT
            self.publisher.publish(msg)

        if self.verbose:
            # Mask out only the reds. Everything else will be black.
            masked = cv2.bitwise_and(blurred, blurred, mask=mask)
            cv2.imshow('Stoplight-masked',
                       cv2.cvtColor(masked, cv2.COLOR_HSV2BGR))
