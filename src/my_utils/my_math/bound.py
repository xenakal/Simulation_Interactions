import math
import numpy as np


def bound_angle_btw_minus_pi_plus_pi(angle):
    if angle is None:
        return None

    if math.fabs(angle) > math.pi:
        return -np.sign(angle) * (math.pi - np.sign(angle) * math.fmod(angle, math.pi))
    return angle
