import shutil
import os
import numpy
from multi_agent.room import *
from multi_agent.agent_region import *

def set_room(scenario):
    # Here by changing only the vectors it is possible to create as many scenario as we want !
    if scenario == -1:
        x_tar = numpy.array([55])
        y_tar = numpy.array([55])
        vx_tar = numpy.array([4])
        vy_tar = numpy.array([4])
        traj_tar = numpy.array(["linear"])
        trajChoice_tar = numpy.array([0])
        size_tar = numpy.array([5])
        label_tar = numpy.array(['target'])
        # Options for the cameras
        x_cam = numpy.array([10])
        y_cam = numpy.array([10])
        angle_cam = numpy.array([75])
        angle_view_cam = numpy.array([60])
        fix_cam = [1]

    elif scenario == 0:
        # Options for the target
        x_tar = numpy.array([55, 200, 40, 150])
        y_tar = numpy.array([55, 140, 280, 150])
        vx_tar = numpy.array([0, 4, 0, 0])
        vy_tar = numpy.array([0, 0, 0, 0])
        traj_tar = numpy.array(['linear', 'linear', 'linear', 'potential_field'])
        trajChoice_tar = numpy.array([0, 0, 0, 0])
        size_tar = numpy.array([5, 5, 5, 5])
        label_tar = numpy.array(['fix', 'fix', 'obstruction', 'fix'])
        t_add = [[0],[0],[0],[0]]
        t_del = [[1000],[1000],[1000],[1000]]
        # Options for the cameras
        x_cam = numpy.array([0, 300, 0, 300, ])
        y_cam = numpy.array([0, 0, 300, 300])
        angle_cam = numpy.array([45, 135, 315, 225])
        angle_view_cam = numpy.array([60, 60, 60, 60])
        fix_cam = [1, 1, 1, 1]

    elif scenario == 1:
        # Options for the cameras
        x_tar = numpy.array([150])
        y_tar = numpy.array([150])
        vx_tar = numpy.array([0])
        vy_tar = numpy.array([0])
        traj_tar = numpy.array(['linear'])
        trajChoice_tar = numpy.array([0])
        size_tar = numpy.array([20])
        label_tar = numpy.array(['fix'])
        t_add = [[0]]
        t_del = [[1000]]
        # Options for the cameras
        x_cam = numpy.array([0, 300, 0, 300, ])
        y_cam = numpy.array([0, 0, 300, 300])
        angle_cam = numpy.array([45, 135, 315, 225])
        angle_view_cam = numpy.array([60, 60, 60, 60])
        fix_cam = [1, 1, 1, 1]

    elif scenario == 2:
        # Options for the target
        x_tar = numpy.array([250, 200, 150, 100, 50, 50, 50, 50, 50, 100, 150, 200, 250, 250, 250, 250])
        y_tar = numpy.array([50, 50, 50, 50, 50, 100, 150, 200, 250, 250, 250, 250, 250, 200, 150, 100])
        trajChoice_tar = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        vx_tar = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        vy_tar = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        traj_tar = numpy.array(
            ['linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'linear',
             'linear', 'linear'
                , 'linear', 'linear', 'linear', 'linear'])
        size_tar = numpy.array([10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10])
        label_tar = numpy.array(['fix', 'fix', 'fix', 'fix', 'fix', 'fix', 'fix', 'fix',
                                 'fix', 'fix', 'fix', 'fix', 'fix', 'fix', 'fix', 'fix'])
        # Options for the cameras
        x_cam = numpy.array([150])
        y_cam = numpy.array([150])
        angle_cam = numpy.array([90])
        angle_view_cam = numpy.array([60])
        fix_cam = [0]

    elif scenario == 3:
        # Options for the cameras
        x_tar = numpy.array([])
        y_tar = numpy.array([])
        vx_tar = numpy.array([])
        vy_tar = numpy.array([])
        traj_tar = numpy.array([])
        trajChoice_tar = numpy.array([0])
        size_tar = numpy.array([20])
        label_tar = numpy.array(['fix'])
        t_add = [[0]]
        t_del = [[1000]]
        # Options for the cameras
        x_cam = numpy.array([0, 300, 0, 300, ])
        y_cam = numpy.array([0, 0, 300, 300])
        angle_cam = numpy.array([45, 135, 315, 225])
        angle_view_cam = numpy.array([60, 60, 60, 60])
        fix_cam = [1, 1, 1, 1]

    elif scenario == 4:
        # Options for the target
        x_tar = numpy.array([30, 40, 45, 30, 120, 200])
        y_tar = numpy.array([30, 40, 30, 60, 155, 20])
        vx_tar = numpy.array([0, 0, 0, 0, 0, 0])
        vy_tar = numpy.array([0, 0, 0, 0, 0, 5])
        traj_tar = numpy.array(['linear', 'linear', 'linear', 'linear', 'linear', 'linear'])
        trajChoice_tar = numpy.array([0, 0, 0, 0, 0, 1])
        size_tar = numpy.array([5, 5, 5, 10, 20, 5])
        label_tar = numpy.array(['fix', 'fix', 'fix', 'fix', 'fix', 'target'])
        # Options for the cameras
        x_cam = numpy.array([150, 20, 20])
        y_cam = numpy.array([150, 20, 250])
        angle_cam = numpy.array([0, 45, -45])
        angle_view_cam = numpy.array([60, 60, 60])
        fix_cam = [1, 1, 1]

    elif scenario == 5:
        # Options for the target
        x_tar = numpy.array([155])
        y_tar = numpy.array([155])
        vx_tar = numpy.array([0])
        vy_tar = numpy.array([0])
        traj_tar = numpy.array(['linear'])
        trajChoice_tar = numpy.array([0])
        size_tar = numpy.array([20])
        label_tar = numpy.array(['fix'])
        t_add = [[0]]
        t_del = [[1000]]
        # Options for the cameras
        x_cam = numpy.array([10, 310])
        y_cam = numpy.array([155, 155])
        angle_cam = numpy.array([0, 180])
        angle_view_cam = numpy.array([60, 60])
        fix_cam = [1, 1, 1]

    elif scenario == 6:
        # Options for the target
        x_tar = numpy.array([155, 20, 30])
        y_tar = numpy.array([155, 20, 50])
        vx_tar = numpy.array([0, 0, 0])
        vy_tar = numpy.array([0, 0, 0])
        traj_tar = numpy.array(['linear', 'linear', 'linear'])
        trajChoice_tar = numpy.array([0, 1, 0])
        size_tar = numpy.array([20, 5, 6])
        label_tar = numpy.array(['fix', 'target', 'obstruction'])
        t_add = [[0],[0],[0]]
        t_del = [[1000],[1000],[1000]]
        # Options for the cameras
        x_cam = numpy.array([0, 300, 150])
        y_cam = numpy.array([155, 155, 0])
        angle_cam = numpy.array([0, 180, 90])
        angle_view_cam = numpy.array([60, 60, 30])
        fix_cam = [1, 1, 1]

    elif scenario == 7:
        # Options for the target
        x_tar = numpy.array([150])
        y_tar = numpy.array([150])
        vx_tar = numpy.array([0])
        vy_tar = numpy.array([0])
        traj_tar = numpy.array(['linear'])
        trajChoice_tar = numpy.array([0])
        size_tar = numpy.array([20])
        label_tar = numpy.array(['fix'])
        t_add = [[0]]
        t_del = [[1000]]
        # Options for the cameras
        x_cam = numpy.array([0])
        y_cam = numpy.array([0])
        angle_cam = numpy.array([45])
        angle_view_cam = numpy.array([60])
        fix_cam = [1]



    else:
        print("this scenario number doesn't exist, sorry...")
        return

    # Creating the room, the target and the camera
    myRoom = Room()
    myRoom.init(x_tar, y_tar, vx_tar, vy_tar, traj_tar, trajChoice_tar,label_tar,size_tar,t_add,t_del)
    myRoom.init_agentCam(x_cam, y_cam, angle_cam, angle_view_cam, fix_cam, myRoom)


    for agent in myRoom.agentCams:
        agent.run()

    return myRoom
