import math
import matplotlib.pyplot as plt
import numpy as np


def rotate_angle(angle, x, y, x_mean, y_mean):
    x_offset = x - x_mean
    y_offset = y - y_mean

    x_rotate = math.cos(angle) * x_offset + math.sin(angle) * y_offset
    y_rotate = -math.sin(angle) * x_offset + math.cos(angle) * y_offset
    return (x_rotate, y_rotate)


def rotate_vector_field_angle(angle, X, Y):
    norm = np.float_power(np.square(X)+np.square(Y),0.5)
    X = norm*np.cos(math.radians(angle))
    Y = norm*np.sin(math.radians(angle))
    return X,Y

def unrotate_angle(angle, x, y, x_mean, y_mean):
    x_rotate = math.cos(angle) * x + math.sin(angle) * y
    y_rotate = -math.sin(angle) * x + math.cos(angle) * y

    x = x_rotate + x_mean
    y = y_rotate + y_mean
    return (x, y)


X = np.arange(0, 8, 0.25)
Y = np.arange(0, 8, 0.25)
X, Y = np.meshgrid(X, Y)

force_x = X
force_y = np.zeros(np.shape(X))


# Plot the surface.
fig = plt.figure(figsize=(12, 8))
fig.suptitle('test', fontsize=17, fontweight='bold', y=0.98)
fig.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(1, 2, 2)

ax1.quiver(X, Y, force_x, force_y)
force_x_rotate,force_y_rotate = rotate_vector_field_angle(45,force_x,force_y)
ax2.quiver(X,Y,force_x_rotate,force_y_rotate)

plt.show()
