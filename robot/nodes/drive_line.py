#!/usr/bin/env python2
from __future__ import division, print_function


class DriveLine(object):
    """Simple singleton to handle wheel speeds while line following."""

    Kp = 0.4 * 8
    Ki = 0
    Kd = 0.1 * 8

    def __init__(self, r, L, verbose=False):
        """Initialize variables for this singleton.

        :param r: The robot wheel radius.
        :param L: The robot half-axle length.
        :param verbose: Should the DriveLine path scrape together enough
                        passion to notify us of basic information? Defaults
                        to False.
        """
        self.verbose = verbose
        self.r = r
        self.r_inv = 1 / r
        self.L = L
        self.e_2 = 0
        self.e_1 = 0
        self.U = 0

    def calcWheelSpeeds(self, w1, w2, difference):
        """Calculate new wheel speeds based on velocity and error."""
        self.__calcPID(difference)
        return self.__calcWheelSpeeds(self.__vConstant(w1, w2))

    def __vConstant(self, w1, w2):
        """Average the given wheel speeds to get the linear forward velocity.

        :param w1: The left wheel speed.
        :param w2: The right wheel speed.
        """
        return self.r * (w1 + w2) / 2.0

    def __calcPID(self, error):
        """Calculate PID and updates error 1 & 2, updates U."""
        P = self.Kp * (error - self.e_1)
        I = self.Ki * (error + self.e_1)
        D = self.Kd * (error - 2 * self.e_1 + self.e_2)
        self.U = self.U + P + I + D
        self.e_2 = self.e_1
        self.e_1 = error
        if self.verbose:
            print('E1:  {}'.format(self.e_1))
            print('E2:  {}'.format(self.e_2))
            print('U:   {}'.format(self.U))

    def __calcWheelSpeeds(self, vel):
        """Calculate & returns w1 and w2."""
        w1, w2 = (self.r_inv * (vel + self.L * self.U),
                  self.r_inv * (vel - self.L * self.U))
        if self.verbose:
            print('Left Wheel:  {}'.format(w1))
            print('Right Wheel: {}'.format(w2))
        return w1, w2


if __name__ == '__main__':
    # TESTING SECTION since we aren't making testing classes
    # Test too far to the left
    print('\nTest too far to the left:')
    print('-----------------------------------------------------')
    diff = 0.2
    DL = DriveLine(5, 10)
    w1, w2 = DL.calcWheelSpeeds(5.0, 5.0, diff)
    print('Diff: {}\n{} {}'.format(diff, w1, w2))
    print('-----------------------------------------------------')

    # Test too far to the right
    print('\nTest too far to the right:')
    print('-----------------------------------------------------')
    diff = -diff
    DL = DriveLine(5, 10)
    w1, w2 = DL.calcWheelSpeeds(5.0, 5.0, diff)
    print('Diff: {}\n{} {}'.format(diff, w1, w2))
    print('-----------------------------------------------------')

    # Test dead-on
    print('\nTest dead-on:')
    print('-----------------------------------------------------')
    diff = 0
    DL = DriveLine(5, 10)
    w1, w2 = DL.calcWheelSpeeds(5.0, 5.0, diff)
    print('Diff: {}\n{} {}'.format(diff, w1, w2))
    print('-----------------------------------------------------')

    # Test correction over time
    print('\nTest correction over time:')
    print('-----------------------------------------------------')
    diff = 0.50
    w1 = 5.0
    w2 = 5.0
    DL = DriveLine(5, 10)
    while diff > 0.01:
        w1, w2 = DL.calcWheelSpeeds(w1, w2, diff)
        diff -= 0.05
        print('Diff: {}\n{} {}\n'.format(diff, w1, w2))
    print('-----------------------------------------------------')
