import math
import random
import re

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



def parse_list(s):
    is_tuple = False
    if s[0] == "(":
        is_tuple = True

    ret_list = []
    s = s[1:-1]

    if "[" in s:
        s = s[1:-1]
        lists = re.split("],\[", s)
        for element in lists:
            ret_list.append(parse_element("[" + str(element) + "]"))
    if "(" in s :
        s = s[1:-1]
        lists = re.split("\),\(", s)
        for element in lists:
            ret_list.append(parse_element("(" + str(element) + ")"))
    else:
        elements = re.split(",", s)
        for element in elements:
            ret_list.append(parse_element(element))

    if is_tuple:
        ret_list = tuple(ret_list)

    return ret_list


def parse_element(s):
    if isinstance(s,str) and len(s) > 0:
        try:
            if s.isdigit():
                return int(s)
            else:
                return float(s)
        except:
                if (s[0] == "[" and s[-1] == "]")or(s[0] == "(" and s[-1] == ")"):
                    return parse_list(s)

    return s


class Item:
    def __init__(self, id=None):
        self.id = id
        self.signature = int(random.random() * 10000000000000000) + 100
        self.attributes_not_to_send=["attributes_not_to_send"]

    def fill_and_parse_attributes(self, s):
        self.fill_attributes_from_str(s)
        self.parse_attributes()

    def parse_attributes(self):
        for key, value in self.__dict__.items():
            if key not in self.attributes_not_to_send:
                self.__dict__[key] = parse_element(value)

    def fill_attributes_from_str(self, s):
        s = s.replace("\n", "")
        s = s.replace(" ", "")

        s = s[len("ITEM_START:"),:]
        s = s[:,-len("ITEM_END:")]

        string_to_parse = ""
        for key, value in self.__dict__.items():
            string_to_parse += key + ":|"
        string_to_parse = string_to_parse[:-1]

        attributes_parse = re.split(string_to_parse, s)
        attributes_parse = attributes_parse[1:]

        item_dictionnary = [(key,value) for key,value in self.__dict__.items() if key not in self.attributes_not_to_send]
        for (key, value), value_parse in zip(item_dictionnary, attributes_parse):
            self.__dict__[key] = value_parse

    def attributes_to_string(self):
        s = "ITEM_START: "
        for key, value in self.__dict__.items():
            if key not in self.attributes_not_to_send:
                s += str(key)+":"+str(value)+" "
        return s +"ITEM_END"


if __name__ == "__main__":
    item = Item("test")
    print(item.attributes_to_string())
    item2 = Item()
    item2.fill_and_parse_attributes(item.attributes_to_string())
    print(item2.attributes_to_string())