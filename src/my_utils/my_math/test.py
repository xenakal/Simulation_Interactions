import math

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np

target_list = [(0,0),(4,4),(2,4)]


def potentiel_rep_def_vector(potentiel,x,y):
    pass


def rotate_angle(angle, x, y):
    x_rotate = math.cos(angle) * x + math.sin(angle) * y
    y_rotate = -math.sin(angle) * x + math.cos(angle) * y
    return (x_rotate, y_rotate)


def potentiel_repulsif(eta,rho_0,X,Y,mean_x,mean_y,var_x,var_y):
    distances = np.power(np.square(X-mean_x)/var_x+np.square(Y-mean_y)/var_y,0.5)
    distances = np.minimum(rho_0,distances)
    potentiels =np.minimum(100, 1 / 2 * eta * np.square(1 / distances - 1 / rho_0))
    return potentiels

fig = plt.figure()
ax = fig.gca(projection='3d')

# Make data.
X = np.arange(-1, 5, 0.25)
Y = np.arange(-1, 5, 0.25)
X, Y = np.meshgrid(X, Y,)

mean_x = 0
mean_y = 0
sigma_x = 1
sigma_y = 1

#Z = 1/(2*np.pi*sigma_x*sigma_y)*np.exp(-np.square(X-mean_x)/(2*np.square(sigma_x))-np.square(Y-mean_y)/(2*np.square(sigma_y)))

Z = np.zeros(np.shape(X))
for target1 in target_list:
    for target2 in target_list:
        if not target1 == target2:
            x1,y1 = target1
            x2,y2 = target2

            x_mean = (x1+x2)/2
            y_mean = (y1+y2)/2
            delta_x =  x1-x2
            delta_y = y1-y2
            angle = math.atan(delta_y/delta_x)

            X,Y = rotate_angle(angle,X,Y)
            #Z = Z + potentiel_repulsif(100,0.8,X, Y, x_mean, y_mean,1+np.abs(delta_x),1+np.abs(delta_y))
            Z = potentiel_repulsif(100,0.8,X, Y, x_mean, y_mean,1+np.abs(delta_x),1+np.abs(delta_y))
            X, Y = rotate_angle(-angle,X,Y)

# Plot the surface.
surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)


# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()

