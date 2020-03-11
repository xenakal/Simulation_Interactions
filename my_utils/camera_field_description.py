import math
import numpy as np

'''
This file containt méthods to compute the field seen by a camera 
'''

def coordinate_Change_from_worldFrame_to_cameraFrame(self, x, y ,x_camera ,y_camera , alpha_camera):
    xi = x - x_camera
    yi = y - y_camera

    xf = math.cos(alpha_camera) * xi + math.sin(alpha_camera) * yi
    yf = -math.sin(alpha_camera) * xi + math.cos(alpha_camera) * yi
    return (xf, yf)