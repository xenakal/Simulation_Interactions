import re


def find_first_char(s, char_list):
    min_index = len(s)
    for elem in char_list:
        if s.find(elem) != -1:
            min_index = min(min_index,s.find(elem))

    if min_index == len(s):
        return ""
    return s[min_index]


def parse_element(s):
    """
            :description
                function to parse a list, a tulpe, a float or an int.
            :param
                1. (string) s -- string to parse

            :return
                1. (list,tuple,int,float)
    """
    if isinstance(s, str) and len(s) > 0:
        try:
            if s.isdigit():
                return int(s)
            else:
                return float(s)
        except:
            if s == "None":
                return None
            elif (s[0] == "[" and s[-1] == "]") or (s[0] == "(" and s[-1] == ")"):
                return parse_list(s)

    return s


def parse_list(s):
    """
            :description
                function to parse a list or a tuple
                ex : [string,string], ...

            :param
                1. (string) s -- string to parse

            :return
                1. (List/tuple) ret_list -- return the list or tuple describe in the strings.
    """

    is_tuple = False
    if s[0] == "(":
        is_tuple = True

    ret_list = []
    s = s[1:-1]

    char_of_interest = ["[","("]
    char_of_interest_resverse =  {"[":"]","(":")"}
    char_of_interest_parse_dict =  {"[":"],\[","(":"\),\("}
    first_char_of_interest = find_first_char(s,char_of_interest)

    if len(s) == 0:
        pass
    elif first_char_of_interest in char_of_interest:
        s = s[1:-1]
        string_to_parse = char_of_interest_parse_dict[first_char_of_interest]
        lists = re.split(string_to_parse, s)
        for element in lists:
            ret_list.append(parse_element(first_char_of_interest + str(element) + char_of_interest_resverse[first_char_of_interest]))
    else:
        elements = re.split(",", s)
        for element in elements:
            ret_list.append(parse_element(element))

    if is_tuple:
        ret_list = tuple(ret_list)

    return ret_list


if __name__ == "__main__":
    print(find_first_char("test(,ffespofos[]", ['E']))
    print(parse_list("[test,test,(tuple,tuple),(tuple)]"))
    print(parse_list("[(test,test),(tuple,tuple),(tuple,tuple)]"))
