import re


def parse_list(s):
    ret_list = []
    s = s[1:-1]

    if "[" in s:
        s = s[1:-1]
        lists = re.split("],\[", s)
        for element in lists:
            ret_list.append(parse_element("[" + str(element) + "]"))
    else:
        elements = re.split(",", s)
        for element in elements:
            ret_list.append(parse_element(element))
    return ret_list


def parse_element(s):
    try:
        if s.isdigit():
            return int(s)
        else:
            return float(s)
    except:
        if s[0] == "[" and s[-1] == "]":
            return parse_list(s)
        return s


class Item:
    def __init__(self, id=None, signature=None):
        self.id = id
        self.signature = signature

    def fill_and_parse_attributes(self, s):
        self.fill_attributes_from_str(s)
        self.parse_attributes()

    def parse_attributes(self):

        for key, value in self.__dict__.items():
            self.__dict__[key] = parse_element(value)

    def fill_attributes_from_str(self, s):
        s = s.replace("\n", "")
        s = s.replace(" ", "")

        string_to_parse = ""
        for key, value in self.__dict__.items():
            string_to_parse += key + ":|"
        string_to_parse = string_to_parse[:-1]

        attributes_parse = re.split(string_to_parse, s)
        attributes_parse = attributes_parse[1:]

        for (key, value), value_parse in zip(self.__dict__.items(), attributes_parse):
            self.__dict__[key] = value_parse

    def attributes_to_string(self):
        s = ""
        for key, value in self.__dict__.items():
            s += str(key) + ":" + str(value) + " "
        return s


if __name__ == "__main__":
    item = Item("test", [[88184.555, 33333], [2225]])
    item2 = Item()
    item2.fill_and_parse_attributes(item.attributes_to_string())
    print(item2.attributes_to_string())
