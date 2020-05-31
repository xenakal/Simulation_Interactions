from src.app import *
from src import constants

"""
map_to_test_name is a list taking multiple maps's name. 
ex: map_to_test_name = ["my_map_1","my_map_2",...]

set the folder in which those maps are located with constants.MapPath.folder
by default in maps
"""

map_to_test_name = ["test1"]

""" Used to specify whether we want to use arguments passed from user. """
use_args = False

"""
Variable here are use to set the desired parameter during the simulation.
"""

"""Kalman centralised VS Kalman distributed to track the targets"""
if not use_args:
    kalman_distributed = [False]
else:
    kalman_distributed = [sys.argv[1] == "T"]

"""Kalman with a model taking:
        - positions = 2 
        - positions and speeds = 4
        - positions,speeds and accelerations = 6
"""
kalman_type = [4]

"""Time at which the simulation should stop, the time to start is eaqual to 0 s"""
t_stop = [80]
"""When many cameras are used, it might be a good idea to slowdown the simulation using a scaling factor < 1"""
t_scale = [1]



index = 0
iteration = 10

while index < iteration:
    print("processing " + str(map_to_test_name[0]) + "etape : " + str(index) + "/" + str(iteration))
    (is_do_previous, is_do_next) = App(map_to_test_name[0], kalman_distributed[0], kalman_type[0],
                                       t_stop[0], t_scale[0]).main()

    index += 1
    if is_do_previous:
       pass
    elif is_do_next:
        pass
    else:
        print("exit completely")
        break

