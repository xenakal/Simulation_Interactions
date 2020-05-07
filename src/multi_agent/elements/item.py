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
    if "(" in s:
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
    if isinstance(s, str) and len(s) > 0:
        try:
            if s.isdigit():
                return int(s)
            else:
                return float(s)
        except:
            if (s[0] == "[" and s[-1] == "]") or (s[0] == "(" and s[-1] == ")"):
                return parse_list(s)

    return s


def create_item_from_string(s):

    s = s.replace("\n", "")
    s = s.replace(" ", "")

    s = s[len(constants.ITEM_START_MARKER):]
    s = s[:-len(constants.ITEM_END_MARKER)]

    item_tag = s[:5]
    s = s[5:]

    class_string = re.search(str(item_tag) + 'item_type:(.*)' + str(item_tag) + 'id', s).group(1)
    item = object_from_string(class_string)

    string_to_parse = ""
    for key, value in item.__dict__.items():
        string_to_parse += item_tag + key + ":|"
    string_to_parse = string_to_parse[:-1]

    attributes_parse = re.split(string_to_parse, s)
    attributes_parse = attributes_parse[1:]

    item_dictionnary = [(key, value) for key, value in item.__dict__.items() if
                        key not in item.attributes_not_to_send]
    for (key, value), value_parse in zip(item_dictionnary, attributes_parse):
        if constants.ITEM_START_MARKER in value_parse:
            item.__dict__[key] = create_item_from_string(value_parse)
        else:
            item.__dict__[key] = parse_element(value_parse)

    return item


def object_from_string(class_string):
    class_substring = re.split("\.", class_string)
    class_substring = class_substring[-1]
    index_end = class_substring.index("'")
    class_substring = class_substring[:index_end]
    import importlib.util

    return eval(class_substring)()


class Item:
    def __init__(self, id=None):
        self.item_type = type(self)
        self.id = id
        self.signature = int(random.random() * 10000000000000000) + 100
        self.attributes_not_to_send = ["attributes_not_to_send"]

    def attributes_to_string(self):
        s = constants.ITEM_START_MARKER + str(self.signature)[:5] + " "
        for key, value in self.__dict__.items():
            if key not in self.attributes_not_to_send:
                if isinstance(value, Item):
                    s += str(self.signature)[:5] + str(key) + ":" + value.attributes_to_string() + " "
                else:
                    s += str(self.signature)[:5] + str(key) + ":" + str(value) + " "
        return s + " " + constants.ITEM_END_MARKER


'''
class ItemTypes:
    keys = ["item", "camera", "agent"]
    values = [Item, MobileCamera, AgentRepresentation]
'''


if __name__ == "__main__":
    item = Item("test")
    print(item.attributes_to_string())
    item2 = create_item_from_string(item.attributes_to_string())
    print(item2.attributes_to_string())
