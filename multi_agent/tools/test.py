import math
from my_utils.line import *
from multi_agent.elements.camera import *


def sort_detected_target(target_list):
    # computation of the distances
    target_list.sort()
    return target_list


target1 = TargetCameraDistance("test", 0)
target2 = TargetCameraDistance("test", -1)
target3 = TargetCameraDistance("test", 5)
target4 = TargetCameraDistance("test", 2)

mylist = []
mylist.append(target1)
mylist.append(target2)
mylist.append(target3)
mylist.append(target4)
mylist = sort_detected_target(mylist)
for elem in mylist:
    print(elem.distance)


def compute_projection(length_projection):
    projection_list = []
    """Placing the view in the cam frame"""
    median_camera = Line(0, 0, 10, 0)
    projection_line = median_camera.linePerp(length_projection, 0)

    beta = math.radians(45)
    """Bound of the field camera"""
    limit_up_camera = Line(0, 0, math.cos(beta), math.sin(beta))
    limit_down_camera = Line(0, 0, math.cos(beta), math.sin(-beta))

    """Projection of the limit on the projection plane"""
    print(projection_line.getSlope())
    print(limit_up_camera.getSlope())

    limit_up_on_projection_line = limit_up_camera.lineIntersection(projection_line)[1]
    limit_down_on_projection_line = limit_down_camera.lineIntersection(projection_line)[1]

    print(limit_up_on_projection_line)
    print(limit_down_on_projection_line)


compute_projection(5)
