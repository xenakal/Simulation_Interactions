from code.app import*
from code import constants



"""
map_to_test_name is a list taking multiple map_to_test's name. 
ex: map_to_test_name = ["my_map_1","my_map_2",...]

set the folder in which those map_to_test are located with constants.MapPath.folder
by default in map_to_test
"""
#constants.MapPath.folder = "to_test"
map_to_test_name = ["My_new_map"]


"""
Variable here are use to set the desired parameter during the simulation.
"""

"""Kalman centralised VS Kalman distributed to track the targets"""
kalman_distributed = [False]

"""Kalman with a model taking:
        - positions = 2 
        - positions and speeds = 4
        - positions,speeds and accelerations = 6
"""
kalman_type = [4]

"""Time at which the simulation should stop, the time to start is eaqual to 0 s"""
t_stop = [20]
"""When many cameras are used, it might be a good idea to slowdown the simulation using a scaling factor < 1"""
t_scale = [1]



for name,kalman_distributed_elem,kalman_type_elem,t_stop_elem,t_scale_elem  in zip(map_to_test_name,kalman_distributed,kalman_type,t_stop,t_scale):
    print("processing "+str(name))
    App(name,kalman_distributed_elem,kalman_type_elem,t_stop_elem,t_scale_elem).main()

