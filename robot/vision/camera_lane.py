from __future__ import division, print_function

import cv2
from std_msgs.msg import Float32

from .camera_base import Camera
from .mask import mask_image


class LaneCamera(Camera):
    """Camera class for lane following."""

    # The portion of the image we focus on. (y-slice, x-slice).
    REGION_OF_INTEREST = (slice(470, 480, None), slice(0, None, None))
    # The threshold value.
    THRESH_VALUE = 70
    # The threshold maximum value.
    THRESH_MAX = 255
    # The white mask sensitivity.
    WHITE_SENSITIVITY = 50

    def process_image(self, hsv_image):
        """Implement lane detection and publishes the lane centroid."""
        # Crop the image to deal only with whatever is directly in front of us.
        hsv_image = hsv_image[self.REGION_OF_INTEREST]

        # Mask out everything but white.
        mask = mask_image(hsv_image, (0, 0, 255 - self.WHITE_SENSITIVITY),
                          (255, self.WHITE_SENSITIVITY, 255))

        if self.verbose:
            cv2.namedWindow('Lane W Mask', cv2.WINDOW_NORMAL)
            cv2.imshow('Lane W Mask', mask)

        # Find contours in the ROI mask itself.
        _, contours, _ = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the biggest contour.
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)

            # Avoid division by zero...
            if M['m00'] != 0:
                # Find the centroid of the biggest contour.
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])

                # Image center => 0.0, left border => -1.0, right border => 1.0
                image_center = hsv_image.shape[1] / 2
                fraction = 0.0
                if cx <= image_center:
                    fraction = (cx - image_center) / image_center
                else:
                    fraction = -(image_center - cx) / image_center

                msg = Float32()
                msg.data = fraction
                self.publisher.publish(msg)
