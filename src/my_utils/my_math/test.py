import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import itertools

def rotate_vector_field_angle(angle, X, Y):
    norm = np.float_power(np.square(X) + np.square(Y), 0.5)
    old_angle = np.arctan2(Y, X)
    X = norm * np.cos(angle + old_angle)
    Y = norm * np.sin(angle + old_angle)
    return X, Y


def rotate_map_from_angle_alpha(angle, x, y, x_mean, y_mean):
    x_offset = x - x_mean
    y_offset = y - y_mean

    x_rotate = math.cos(angle) * x_offset + math.sin(angle) * y_offset
    y_rotate = -math.sin(angle) * x_offset + math.cos(angle) * y_offset
    return x_rotate, y_rotate


def unrotate_map_from_angle_alpha(angle, x, y, x_mean, y_mean):
    x_rotate = math.cos(angle) * x + math.sin(angle) * y
    y_rotate = -math.sin(angle) * x + math.cos(angle) * y

    x = x_rotate + x_mean
    y = y_rotate + y_mean
    return x, y


def potentiel_repulsif_droite(eta, rho_0, y, mean_y, var_y):
    return potentiel_repulsif_point(eta, rho_0, y, 0, mean_y, 0, var_y, 1)


def force_repulsive_droite(eta, rho_0, y, mean_y, var_y):
    return force_repulsive_point(eta, rho_0, y, 0, mean_y, 0, var_y, 1)


def potentiel_repulsif_point(eta, rho_0, x, y, mean_x, mean_y, var_x, var_y):
    distances = np.power(np.square(x - mean_x) / var_x + np.square(y - mean_y) / var_y, 0.5)
    distances = np.where(distances > 0.01 * rho_0, distances, rho_0)
    distances = np.where(distances <= rho_0, distances, rho_0)
    potentiels = np.minimum(50, 0.5 * eta * np.square(1 / distances - 1 / rho_0))
    # potentiels = 1/(2*np.pi*var_x*var_y)*np.exp(-np.square(X-mean_x)/(2*np.square(var_x))-np.square(Y-mean_y)/(2*np.square(var_y)))
    return potentiels


def force_repulsive_point(eta, rho_0, X, Y, mean_x, mean_y, var_x, var_y):
    distances = np.power(np.square(X - mean_x) / var_x + np.square(Y - mean_y) / var_y, 0.5)
    distances = np.where(distances > 0.1 * rho_0, distances, rho_0)
    distances = np.where(distances <= rho_0, distances, rho_0)

    angle = np.arctan2(Y - mean_y, X - mean_x)
    force_x = np.minimum(50, 0.5 * eta * (1 / distances - 1 / rho_0) * np.square(1 / rho_0)) * np.cos(angle)
    force_y = np.minimum(50, 0.5 * eta * (1 / distances - 1 / rho_0) * np.square(1 / rho_0)) * np.sin(angle)
    return force_x, force_y

def compute_repulsive_potential(target_list):
    X = np.arange(0, 8, 0.05)
    Y = np.arange(0, 8, 0.05)
    X, Y = np.meshgrid(X, Y)

    potential_field = np.zeros(np.shape(X))
    force_x = np.zeros(np.shape(X))
    force_y = np.zeros(np.shape(X))

    for targets in itertools.combinations(target_list, 2):
        target1, target2 = targets
        x1, y1, radius1 = target1
        x2, y2, radius2 = target2

        x_mean = (x1 + x2) / 2
        y_mean = (y1 + y2) / 2

        delta_x = x1 - x2
        delta_y = y1 - y2

        distance = np.power(np.square(x1 - x2) + np.square(y1 - y2), 0.5)
        angle = math.atan2(delta_y, delta_x)

        """First rotation to place x-axis between the to targets"""
        X, Y = rotate_map_from_angle_alpha(angle, X, Y, x_mean, y_mean)

        """Computation from the vectors"""
        delta_force_x, delta_force_y = force_repulsive_droite(10, max(radius1,radius2), Y, 0, 1)
        delta_force_x_rotate, delta_force_y_rotate = rotate_vector_field_angle(angle + math.pi / 2, delta_force_x,
                                                                               delta_force_y)
        force_x += delta_force_x_rotate
        force_y += delta_force_y_rotate

        """Computation from the field"""
        potential_field = potential_field + potentiel_repulsif_droite(10, 0.5, Y, 0, 1)
        X, Y = unrotate_map_from_angle_alpha(-angle, X, Y, x_mean, y_mean)

        """Adding repulsive potential where targets"""
        delta_force_x, delta_force_y = force_repulsive_point(10, radius1, X, Y, x1, y1, 1, 1)
        force_x += delta_force_x
        force_y += delta_force_y
        delta_force_x, delta_force_y = force_repulsive_point(10, radius2, X, Y,x2, y2, 1, 1)
        force_x += delta_force_x
        force_y += delta_force_y
        potential_field = potential_field + potentiel_repulsif_point(10, radius1, X, Y, x1, y1, 1, 1)
        potential_field = potential_field + potentiel_repulsif_point(10, radius2, X, Y, x2, y2, 1, 1)

    return X,Y,potential_field,force_x,force_y

def plot_repulive_field(X,Y,potential_field,force_x,force_y):
    # Plot the surface.
    fig = plt.figure(figsize=(12, 8))
    fig.suptitle('test', fontsize=17, fontweight='bold', y=0.98)
    fig.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')

    ax2 = fig.add_subplot(1, 2, 2)

    surf = ax1.plot_surface(X, Y, potential_field, cmap=cm.coolwarm,
                                linewidth=0, antialiased=False)

    ax2.quiver(X, Y, force_x, force_y)
    plt.show()


target_list = [(2, 1,.3), (1, 5,.3), (7, 3,.3)]
X,Y,Z,force_x,force_y = compute_repulsive_potential(target_list)
plot_repulive_field(X,Y,Z,force_x,force_y)