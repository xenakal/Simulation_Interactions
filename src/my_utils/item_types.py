import re
from src import constants
from src.my_utils.string_operations import parse_element
from src.my_utils.item import Item
from src.multi_agent.elements.mobile_camera import MobileCameraRepresentation
from src.multi_agent.elements.target import TargetRepresentation
from src.multi_agent.agent.agent_interacting_room_camera_representation import AgentCamRepresentation


def get_class_name_on_class_source_name(class_string):
    class_substring = re.split("\.", class_string)
    class_substring = class_substring[-1]
    index_end = class_substring.index("'")
    class_substring = class_substring[:index_end]
    return class_substring


def create_item_from_string(s):
    """
           :description
                Create a object based on a string description.
                The string desciption is a created thanks to the function attributes_to_string from the class item

            :param
                1. (string) s -- string to parse

            :return
                1. (object) item -- a object Item or an inheritance class from Item
    """
    s = s.replace("\n", "")
    s = s.replace(" ", "")

    s = s[len(constants.ITEM_START_MARKER):]
    s = s[:-len(constants.ITEM_END_MARKER)]

    item_tag = s[:len(constants.ITEM_CONSTANT_TAG_MARKER) + 5]
    s = s[len(constants.ITEM_CONSTANT_TAG_MARKER) + 5:]

    class_string = re.search(str(item_tag) + 'item_type:(.*)' + str(item_tag) + 'id', s).group(1)
    class_substring = get_class_name_on_class_source_name(class_string)

    item = None
    for key, value in ItemType.dictionary_item_types.items():
        if eval(class_substring) == type(value()):
            item = value()

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


class ItemType:
    ItemEstimation = "item_estimation"
    AgentEstimation = "agent_estimation"
    TargetEstimation = "target_estimation"
    CameraEstimation = "camera_estimation"

    keys_string_names = [ItemEstimation, TargetEstimation, AgentEstimation, CameraEstimation]
    values_class_names = [Item,TargetRepresentation, AgentCamRepresentation, MobileCameraRepresentation]
    dictionary_item_types = dict(zip(keys_string_names, values_class_names))
