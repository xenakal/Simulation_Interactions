import random
import re

from src import constants
from src.my_utils.string_operations import parse_element


def create_anonymus_item_from_string(s):
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

    all_keys_values = re.split(str(item_tag), s)
    all_keys_values = all_keys_values[1:]
    keys = []
    values = []

    for key_value in all_keys_values:
        key_value_split = re.split(":", key_value)
        keys.append(key_value_split[0])

        if constants.ITEM_START_MARKER in key_value:
            values.append(create_anonymus_item_from_string(key_value[len(key_value_split[0]) + 1:]))
        else:
            values.append(parse_element(key_value_split[1]))

    item_dict = {}
    for key, value in zip(keys, values):
        item_dict[key] = value

    item_anonymous = type("", (object,), item_dict)()
    return item_anonymous


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
    """
           :description
                Create a object based on the file location string.

            :param
                1. (string) class_string -- string referring to the class location

            :return
                1. (object) eval(class_substring)() -- a object Item or an inheritance class from
                                                        Item, all parameters instanciate to their default values.
    """
    class_substring = re.split("\.", class_string)
    class_substring = class_substring[-1]
    index_end = class_substring.index("'")
    class_substring = class_substring[:index_end]
    # TODO - to change
    from src.multi_agent.agent.agent_interacting_room_camera import AgentCamRepresentation
    from src.multi_agent.elements.mobile_camera import MobileCameraRepresentation
    from src.multi_agent.elements.target import TargetRepresentation, Target
    from src.user_fct.element_user import ItemUser
    return eval(class_substring)()


class Item:
    """
                Class Item

                Description : General class

                    :param
                        1. (int)      id                       -- numeric value to recognize the target easily

                    :attibutes
                        1. (type)     type                     -- Item type (here Item)
                        2. (int)      id                       -- numeric value to recognize the target easily
                        3. (int)      signature                -- numeric value to identify the target
                        4. ([String]) attributes_not_to_send   -- list from attribues that are not be in attributes_to_string

                    :notes
                    This class is a generic class. It is possible to place each attributes in a string  with
                    the function attributes_to_string. The reverse operation is achieved using the static function
                    create_item_from_string(s)
    """

    def __init__(self, id=None):
        self.item_type = type(self)
        self.id = id
        self.signature = int(random.random() * 10000000000000000) + 100

        self.attributes_not_to_txt = ["attributes_not_to_send", "attributes_not_to_txt"]
        self.attributes_not_to_send = ["attributes_not_to_send", "attributes_not_to_txt"]

    def attributes_to_string(self):
        """
                  :description
                       Create a object based on the file location string.

                   :return
                    1. (string) s -- string representation from every attribues from item except the one present in self.attributes_not_to_send
           """
        s = constants.ITEM_START_MARKER + constants.ITEM_CONSTANT_TAG_MARKER + str(self.signature)[:5] + " "
        for key, value in self.__dict__.items():
            if key not in self.attributes_not_to_send:
                if isinstance(value, Item):
                    s += constants.ITEM_CONSTANT_TAG_MARKER + str(self.signature)[:5] + str(
                        key) + ":" + value.attributes_to_string() + " "
                else:
                    s += constants.ITEM_CONSTANT_TAG_MARKER + str(self.signature)[:5] + str(key) + ":" + str(
                        value) + " "
        return s + constants.ITEM_END_MARKER

    def load_from_attributes_to_string(self, s):
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

        string_to_parse = ""
        for key, value in self.__dict__.items():
            string_to_parse += item_tag + key + ":|"
        string_to_parse = string_to_parse[:-1]

        attributes_parse = re.split(string_to_parse, s)
        attributes_parse = attributes_parse[1:]

        item_dictionnary = [(key, value) for key, value in self.__dict__.items() if
                            key not in self.attributes_not_to_send]

        for (key, value), value_parse in zip(item_dictionnary, attributes_parse):
            if constants.ITEM_START_MARKER in value_parse:
                self.__dict__[key] = create_item_from_string(value_parse)
            else:
                self.__dict__[key] = parse_element(value_parse)

    def save_to_txt(self):
        """
                         :description
                              Create a object based on the file location string.

                          :return
                           1. (string) s -- string representation from every attribues from item except the one present in self.attributes_not_to_send
                  """
        s = ""
        for key, value in self.__dict__.items():
            if key not in self.attributes_not_to_txt:
                if isinstance(value, Item):
                    s += str(key) + ":" + str(type(value)) + " "
                else:
                    s += str(key) + ":" + str(value) + " "

        return s

    def load_from_save_to_txt(self, s):
        """
                      :description
                           Create a object based on a string description.
                           The string desciption is a created thanks to the function attributes_to_string from the class self

                       :param
                           1. (string) s -- string to parse

                       :return
                           1. (object) self -- a object Item or an inheritance class from Item
        """
        s = s.replace("\n", "")
        s = s.replace(" ", "")

        string_to_parse = ""
        for key, value in self.__dict__.items():
            string_to_parse += key + ":|"
        string_to_parse = string_to_parse[:-1]

        attributes_parse = re.split(string_to_parse, s)
        attributes_parse = attributes_parse[1:]

        item_dictionnary = [(key, value) for key, value in self.__dict__.items() if
                            key not in self.attributes_not_to_txt]

        for (key, value), value_parse in zip(item_dictionnary, attributes_parse):
            self.__dict__[key] = parse_element(value_parse)
        return self


if __name__ == "__main__":
    """Example where item2 is create  thanks to item string"""
    item1 = Item(1)
    print(item1.save_to_txt())
    print(item1.attributes_to_string())
    item2 = Item()
    item2.load_from_attributes_to_string(item1.attributes_to_string())
    print(item2.save_to_txt())

    item3 = Item()
    item3 = item3.load_from_save_to_txt(item2.save_to_txt())
    print(item3.save_to_txt())
