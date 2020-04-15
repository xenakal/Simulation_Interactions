from src.app import *
from src import constants

"""
map_to_test_name is a list taking multiple maps's name. 
ex: map_to_test_name = ["my_map_1","my_map_2",...]

set the folder in which those maps are located with constants.MapPath.folder
by default in maps
"""

map_to_test_name = ["My_new_map", "map", "map2", "map3", "map4"]

""" Used to specify whether we want to use arguments passed from user. """
use_args = False

"""
Variable here are use to set the desired parameter during the simulation.
"""

"""Kalman centralised VS Kalman distributed to track the targets"""
if not use_args:
    kalman_distributed = [False, False, False, False, False]
else:
    kalman_distributed = [sys.argv[1] == "T"]

"""Kalman with a model taking:
        - positions = 2 
        - positions and speeds = 4
        - positions,speeds and accelerations = 6
"""
kalman_type = [4, 4, 4, 4, 4]

"""Time at which the simulation should stop, the time to start is eaqual to 0 s"""
t_stop = [500, 500, 500, 500, 500]
"""When many cameras are used, it might be a good idea to slowdown the simulation using a scaling factor < 1"""
t_scale = [1, 1, 1, 1, 1]

index = 0
while index < len(map_to_test_name):

    print("processing " + str(map_to_test_name[index]))
    (is_do_previous, is_do_next) = App(map_to_test_name[index], kalman_distributed[index], kalman_type[index],
                                       t_stop[index], t_scale[index]).main()

    if is_do_previous:
        index -= 1
        if index < 0:
            index = 0

    elif is_do_next:
        index += 1
    else:
        print("exit complietly")
        break
