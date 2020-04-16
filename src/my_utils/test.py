import math
import numpy as np

angle = math.radians(240)
print(math.degrees(-np.sign(angle)*(math.pi - np.sign(angle)*math.fmod(angle,math.pi))))
angle = math.radians(540)
print(math.degrees(-np.sign(angle)*(math.pi - np.sign(angle)*math.fmod(angle,math.pi))))
angle = math.radians(-240)
print(math.degrees(-np.sign(angle)*(math.pi - np.sign(angle)*math.fmod(angle,math.pi))))


