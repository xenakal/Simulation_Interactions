import math
import numpy as np
from src import constants
from src.my_utils.constant_class import ConfidenceFunction
from src.my_utils.my_math.line import Line
import matplotlib.pyplot as plt

def evaluate_confidence(error, delta_time):
   return evaluate_confidence_choice(error,delta_time,constants.CONFIDENCE_FUNCTION_CHOICE)

def evaluate_confidence_choice(error, delta_time,choice):
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
    if ConfidenceFunction.EXPONENTIAL_DECAY == choice:
        if constants.CONFIDENCE_MIN_VALUE >= 1:
            time_constant = -t_thresh / math.log(pt2[1] / pt1[1])
        else:
            time_constant = t_thresh / 5

        delta_t_due_to_amplitude = -time_constant * math.log(amplitude / pt1[1])
        delta_time += delta_t_due_to_amplitude
        ret_confidence = pt1[1] * math.exp(-delta_time / time_constant)

    elif ConfidenceFunction.EXPONENTIAL_REVERSE_DECAY == choice:
        ret_confidence = constants.CONFIDENCE_MAX_VALUE-evaluate_confidence_choice(error,constants.CONFIDENCE_TIME_TO_REACH_MIN_VALUE-delta_time,ConfidenceFunction.EXPONENTIAL_DECAY)

    elif ConfidenceFunction.LINEAR_DECAY == choice:
        if pt1[1] > pt2[1]:
            line = Line(pt1[0], pt1[1], pt2[0], pt2[1])
            delta_t_due_to_amplitude = line.compute_x(amplitude)
            delta_time += delta_t_due_to_amplitude
            ret_confidence = line.compute_y(delta_time, line)
        else:
            ret_confidence = constants.CONFIDENCE_MIN_VALUE

    elif ConfidenceFunction.STEP == choice:
        if delta_time < t_thresh:
            ret_confidence = amplitude
        else:
            ret_confidence = constants.CONFIDENCE_MIN_VALUE

    return min(max(ret_confidence, constants.CONFIDENCE_MIN_VALUE),
               constants.CONFIDENCE_MAX_VALUE)


if __name__ == "__main__":
    constants.CONFIDENCE_MIN_VALUE = 0
    constants.CONFIDENCE_MAX_VALUE = 100
    constants.CONFIDENCE_THRESHOLD = 30


    x = np.linspace(0,constants.CONFIDENCE_TIME_TO_REACH_MIN_VALUE+2,100)
    tresh_value = np.ones(np.size(x))*constants.CONFIDENCE_THRESHOLD
    max_value = np.ones(np.size(x))*constants.CONFIDENCE_MAX_VALUE
    min_value = np.ones(np.size(x)) * constants.CONFIDENCE_MIN_VALUE

    y_step = []
    y_linear = []
    y_exponential = []
    y_exponential_reverse = []
    for value in x:
        y_step.append(evaluate_confidence_choice(0.1, value, ConfidenceFunction.STEP))
        y_linear.append(evaluate_confidence_choice(0.1,value,ConfidenceFunction.LINEAR_DECAY ))
        y_exponential.append(evaluate_confidence_choice(0.1, value, ConfidenceFunction.EXPONENTIAL_DECAY))
        y_exponential_reverse.append(evaluate_confidence_choice(0.1, value, ConfidenceFunction.EXPONENTIAL_REVERSE_DECAY))

    fig = plt.figure(figsize=(16, 8))

    ax0 = fig.add_subplot(1,1, 1)
    ax0.xaxis.set_tick_params(labelsize=20)
    ax0.yaxis.set_tick_params(labelsize=20)

    ax0.plot(x, tresh_value, '--',color='black',linewidth = 4)
    ax0.plot(x, min_value, '--',color='red',linewidth = 4)
    ax0.plot(x, max_value, '--',color='red',linewidth = 4)

    ax0.plot(x, y_step,linewidth = 2)
    ax0.plot(x, y_linear,linewidth = 2)
    ax0.plot(x, y_exponential,linewidth = 2)
    ax0.plot(x, y_exponential_reverse,linewidth = 2)

    ax0.grid("on")
    ax0.set_xlabel("time [s]", fontsize=20)
    ax0.set_ylabel("confidence score", fontsize=20)
    ax0.set_title("Confidence score evolution with respect to time", fontsize=25, fontweight='bold')
    ax0.legend(["Threshold", "Max","Min","Step","Linear","Exponential","Exponential inverted"],loc='upper right',fontsize=18)


    plt.show()
