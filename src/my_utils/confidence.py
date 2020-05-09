import math

from src import constants
from src.my_utils.constant_class import ConfidenceFunction
from src.my_utils.my_math.line import Line


def evaluate_confidence(error, delta_time):
    """Method to modify the value of the confidence based on severals parameters"""
    ret_confidence = constants.CONFIDENCE_MIN_VALUE

    """Kalman dependency"""
    amplitude = (1 / math.pow(error, 2))

    if amplitude > constants.CONFIDENCE_MAX_VALUE:
        amplitude = constants.CONFIDENCE_MAX_VALUE
    t_thresh = constants.CONFIDENCE_TIME_TO_REACH_MIN_VALUE
    pt1 = (0, constants.CONFIDENCE_MAX_VALUE)
    pt2 = (t_thresh, constants.CONFIDENCE_MIN_VALUE)
    if pt1[1] < pt2[1]:
        return ret_confidence

    """Time dependency"""
    if ConfidenceFunction.EXPONENTIAL_DECAY == constants.CONFIDENCE_FUNCTION_CHOICE:
        if constants.CONFIDENCE_MIN_VALUE >= 1:
            time_constant = -t_thresh / math.log(pt2[1] / pt1[1])
        else:
            time_constant = t_thresh / 5

        delta_t_due_to_amplitude = -time_constant * math.log(amplitude / pt1[1])
        delta_time += delta_t_due_to_amplitude
        ret_confidence = pt1[1] * math.exp(-delta_time / time_constant)

    elif ConfidenceFunction.EXPONENTIAL_REVERSE_DECAY == constants.CONFIDENCE_FUNCTION_CHOICE:

        pass

    elif ConfidenceFunction.LINEAR_DECAY == constants.CONFIDENCE_FUNCTION_CHOICE:
        if pt1[1] > pt2[1]:
            line = Line(pt1[0], pt1[1], pt2[0], pt2[1])
            delta_t_due_to_amplitude = line.compute_x(amplitude)
            delta_time += delta_t_due_to_amplitude
            ret_confidence = line.compute_y(delta_time, line)
        else:
            ret_confidence = constants.CONFIDENCE_MIN_VALUE

    elif ConfidenceFunction.STEP == constants.CONFIDENCE_FUNCTION_CHOICE:
        if delta_time < t_thresh:
            ret_confidence = amplitude
        else:
            ret_confidence = constants.CONFIDENCE_MIN_VALUE

    return min(max(ret_confidence, constants.CONFIDENCE_MIN_VALUE),
               constants.CONFIDENCE_MAX_VALUE)