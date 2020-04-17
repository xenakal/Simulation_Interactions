import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import itertools
from src import constants
from src.my_utils.constant_class import*
from src.my_utils.my_math.line import distance_btw_two_point




class PotentialType:
    Repulsive_potential = 1
    Attractive_potential = 2


class PotentialShape:
    Circular = 0
    Linear_X_direction = 1
    Linear_Y_direction = 2


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


def define_potential_shape(shape, X=None, mean_x=None, var_x=None, Y=None, mean_y=None, var_y=None, rho_0=None):
    if shape == PotentialShape.Circular and not X is None and not Y is None:
        distances = np.power(np.square(X - mean_x) / var_x + np.square(Y - mean_y) / var_y, 0.5)
        angle = np.arctan2(Y - mean_y, X - mean_x)
    elif shape == PotentialShape.Linear_X_direction and not Y is None:
        distances = np.square((Y - mean_y) / var_y)
        angle = np.arctan2(Y - mean_y, 0)
    elif shape == PotentialShape.Linear_Y_direction and not X is None:
        distances = np.square((X - mean_x) / var_x)
        angle = np.arctan2(0, X - mean_x)
    else:
        print("define_potential_shape : choice not found or values not set correctly")
        if not X is None:
            distances = np.zeros(np.shape(X))
            angle = distances
        elif not Y is None:
            distances = np.zeros(np.shape(Y))
            angle = distances
        else:
            distances = 0
            angle = distances
    return distances, angle


def define_potential_type(choix, distances, xi=None, eta=None, rho_0=None):
    if choix == PotentialType.Repulsive_potential:
        distances = np.where(distances > 0.001 * rho_0, distances, rho_0)
        distances = np.where(distances <= rho_0, distances, rho_0)
        return 0.5 * eta * np.square(1 / distances - 1 / rho_0)
    elif choix == PotentialType.Attractive_potential:
        return 0.5 * xi * np.square(distances)
    else:
        print("error potential type note found")


def define_grad_potential_type(choix, distances, xi=None, eta=None, rho_0=None):
    if choix == PotentialType.Repulsive_potential:
        distances = np.where(distances > 0.001 * rho_0, distances, rho_0)
        distances = np.where(distances <= rho_0, distances, rho_0)
        return 0.5 * eta * (1 / distances - 1 / rho_0) * np.square(1 / rho_0)
    elif choix == PotentialType.Attractive_potential:
        return -xi * distances
    else:
        print("error potential type not found")


def compute_part_of_potential_field(field_type, shape, X=None, Y=None, mean_x=None, mean_y=None, var_x=None, var_y=None,
                                    xi=None, eta=None, rho_0=None):
    distances, angle = define_potential_shape(shape=shape, X=X, Y=Y, mean_x=mean_x, mean_y=mean_y, var_x=var_x,
                                              var_y=var_y, rho_0=rho_0)
    potential = define_potential_type(field_type, distances, xi=xi, eta=eta, rho_0=rho_0)
    return potential


def compute_part_of_grad_potential_field(field_type, shape, X=None, Y=None, mean_x=None, mean_y=None, var_x=None,
                                         var_y=None, xi=None, eta=None, rho_0=None):
    distances, angle = define_potential_shape(shape=shape, X=X, Y=Y, mean_x=mean_x, mean_y=mean_y, var_x=var_x,
                                              var_y=var_y, rho_0=rho_0)
    grad_x = define_grad_potential_type(field_type, distances, xi=xi, eta=eta, rho_0=rho_0) * np.cos(angle)
    grad_y = define_grad_potential_type(field_type, distances, xi=xi, eta=eta, rho_0=rho_0) * np.sin(angle)
    return grad_x, grad_y


def compute_grad_potential_for_a_given_list(target_list, X, Y, field_type, barrier_type, xi=None, eta=None, rho_0=None):
    force_x = np.zeros(np.shape(X))
    force_y = np.zeros(np.shape(X))

    rho_0_None = False
    if rho_0 is None:
        rho_0_None = True

    if target_list == []:
        return force_x, force_y

    elif len(target_list) == 1:
        x, y, radius = target_list[0]
        if rho_0_None:
            rho_0 = radius

        delta_force_x, delta_force_y = compute_part_of_grad_potential_field(
            field_type=field_type, shape=PotentialShape.Circular, X=X, mean_x=x, var_x=1,
            Y=Y, mean_y=y, var_y=1, xi=xi, eta=eta, rho_0=rho_0)
        force_x += delta_force_x
        force_y += delta_force_y

        return force_x, force_y

    else:
        for target in target_list:
            x, y, radius = target
            if rho_0_None:
                rho_0 = radius
            delta_force_x, delta_force_y = compute_part_of_grad_potential_field(
                field_type=field_type, shape=PotentialShape.Circular, X=X, mean_x=x, var_x=1,
                Y=Y, mean_y=y, var_y=1, xi=xi, eta=eta, rho_0=rho_0)
            force_x += delta_force_x
            force_y += delta_force_y

        for targets in itertools.combinations(target_list, 2):
            target1, target2 = targets
            x1, y1, radius1 = target1
            x2, y2, radius2 = target2

            if rho_0_None:
                rho_0 = max(radius1, radius2)

            """First rotation to place x-axis between the to targets"""
            x_mean = (x1 + x2) / 2
            y_mean = (y1 + y2) / 2
            delta_x = x1 - x2
            delta_y = y1 - y2
            distance = distance_btw_two_point(x1, y1, x2, y2)
            angle = math.atan2(delta_y, delta_x)
            X, Y = rotate_map_from_angle_alpha(angle, X, Y, x_mean, y_mean)
            """Computation from the vectors"""
            delta_force_x, delta_force_y = np.zeros(np.shape(force_x)), np.zeros(np.shape(force_y))
            if barrier_type == PotentialBarrier.Hard:
                delta_force_x, delta_force_y = compute_part_of_grad_potential_field(field_type=field_type,
                                                                                    shape=PotentialShape.Linear_X_direction,
                                                                                    Y=Y, mean_y=0, var_y=1, xi=xi,
                                                                                    eta=eta,
                                                                                    rho_0=rho_0)
            elif barrier_type == PotentialBarrier.Smooth:
                delta_force_x, delta_force_y = compute_part_of_grad_potential_field(
                    field_type=field_type, shape=PotentialShape.Circular, X=X, mean_x=0,
                    var_x=1 + constants.COEFF_VAR_X * distance,
                    Y=Y, mean_y=0, var_y=1 + constants.COEFF_VAR_Y * distance, xi=xi, eta=eta, rho_0=rho_0)

            elif barrier_type == PotentialBarrier.Combine:

                delta_force_x_hard, delta_force_y_hard = compute_part_of_grad_potential_field(field_type=field_type,
                                                                                              shape=PotentialShape.Linear_X_direction,
                                                                                              Y=Y, mean_y=0, var_y=1,
                                                                                              xi=xi,
                                                                                              eta=eta,
                                                                                              rho_0=rho_0)

                delta_force_x_smooth, delta_force_y_smooth = compute_part_of_grad_potential_field(
                    field_type=field_type, shape=PotentialShape.Circular, X=X, mean_x=0,
                    var_x=1 + constants.COEFF_VAR_X * distance,
                    Y=Y, mean_y=0, var_y=1 + constants.COEFF_VAR_Y * distance, xi=xi,
                    eta=eta, rho_0=rho_0)

                delta_force_x, delta_force_y = delta_force_x_hard * (
                            1 - constants.COMBINE_MODE_PROP) + delta_force_x_smooth * constants.COMBINE_MODE_PROP, delta_force_y_hard * (
                                                           1 - constants.COMBINE_MODE_PROP) + delta_force_y_smooth * constants.COMBINE_MODE_PROP
            elif barrier_type == PotentialBarrier.Not_use:
                pass

            delta_force_x_rotate, delta_force_y_rotate = rotate_vector_field_angle(angle, delta_force_x,
                                                                                   delta_force_y)
            force_x += delta_force_x_rotate
            force_y += delta_force_y_rotate
            "Back to orignal ref"
            X, Y = unrotate_map_from_angle_alpha(-angle, X, Y, x_mean, y_mean)

        return force_x, force_y


def compute_potential_for_a_given_list(target_list, X, Y, field_type, barrier_type, xi=None, eta=None, rho_0=None):
    potential_field = np.zeros(np.shape(X))

    rho_0_None = False
    if rho_0 is None:
        rho_0_None = True

    if target_list == []:
        print("test")
        return potential_field

    elif len(target_list) == 1:
        x, y, radius = target_list[0]
        if rho_0_None:
            rho_0 = radius

        potential_field += compute_part_of_potential_field(field_type=field_type,
                                                           shape=PotentialShape.Circular,
                                                           X=X, mean_x=x, var_x=1,
                                                           Y=Y, mean_y=y, var_y=1,
                                                           xi=xi, eta=eta, rho_0=rho_0)
        return potential_field

    else:
        for target in target_list:
            x, y, radius = target
            if rho_0_None:
                rho_0 = radius

            potential_field += compute_part_of_potential_field(field_type=field_type,
                                                               shape=PotentialShape.Circular,
                                                               X=X, mean_x=x, var_x=1,
                                                               Y=Y, mean_y=y, var_y=1,
                                                               xi=xi, eta=eta, rho_0=rho_0)

        for targets in itertools.combinations(target_list, 2):
            target1, target2 = targets
            x1, y1, radius1 = target1
            x2, y2, radius2 = target2

            if rho_0_None:
                rho_0 = max(radius1, radius2)

            """First rotation to place x-axis between the to targets"""
            x_mean = (x1 + x2) / 2
            y_mean = (y1 + y2) / 2
            delta_x = x1 - x2
            delta_y = y1 - y2
            distance = distance_btw_two_point(x1, y1, x2, y2)
            angle = math.atan2(delta_y, delta_x)
            X, Y = rotate_map_from_angle_alpha(angle, X, Y, x_mean, y_mean)

            """Computation from the field"""
            if barrier_type == PotentialBarrier.Hard:
                potential_field += compute_part_of_potential_field(field_type=field_type,
                                                                   shape=PotentialShape.Linear_X_direction,
                                                                   Y=Y, mean_y=0, var_y=1, xi=xi, eta=eta,
                                                                   rho_0=rho_0)

            elif barrier_type == PotentialBarrier.Smooth:
                potential_field += compute_part_of_potential_field(field_type=field_type,
                                                                   shape=PotentialShape.Circular,
                                                                   X=X, mean_x=0,
                                                                   var_x=1 + constants.COEFF_VAR_X * distance,
                                                                   Y=Y, mean_y=0,
                                                                   var_y=1 + constants.COEFF_VAR_Y * distance,
                                                                   xi=xi, eta=eta, rho_0=rho_0)

            elif barrier_type == PotentialBarrier.Combine:
                potential_field += (1 - constants.COMBINE_MODE_PROP) * compute_part_of_potential_field(
                    field_type=field_type,
                    shape=PotentialShape.Linear_X_direction,
                    Y=Y, mean_y=0, var_y=1, xi=xi, eta=eta,
                    rho_0=rho_0)

                potential_field += constants.COMBINE_MODE_PROP * compute_part_of_potential_field(field_type=field_type,
                                                                                                 shape=PotentialShape.Circular,
                                                                                                 X=X, mean_x=0,
                                                                                                 var_x=1 + constants.COEFF_VAR_X * distance,
                                                                                                 Y=Y, mean_y=0,
                                                                                                 var_y=1 + constants.COEFF_VAR_Y * distance,
                                                                                                 xi=xi, eta=eta,
                                                                                                 rho_0=rho_0)
            elif barrier_type == PotentialBarrier.Not_use:
                pass

            "Back to orignal ref"
            X, Y = unrotate_map_from_angle_alpha(-angle, X, Y, x_mean, y_mean)

        return potential_field



def compute_potential_gradient(X,Y,target_list,obstacle_list):
    attractive_force_x, attractive_force_y = compute_grad_potential_for_a_given_list(target_list, X, Y,
                                                                                     PotentialType.Attractive_potential,
                                                                                     constants.BARRIER_TYPE,
                                                                                     xi=constants.XI, eta=constants.ETA,
                                                                                     rho_0=-1)
    repulsive_force_x, repulsive_force_y = compute_grad_potential_for_a_given_list(obstacle_list, X,Y,
                                                                                   PotentialType.Repulsive_potential,
                                                                                   constants.BARRIER_TYPE,
                                                                                   xi=constants.XI, eta=constants.ETA,
                                                                                   rho_0=None)

    force_x = attractive_force_x + repulsive_force_x
    force_y = attractive_force_y + repulsive_force_y

    return force_x, force_y

def compute_potential(X,Y,target_list,obstacle_list):
    attractive_potential_field = compute_potential_for_a_given_list(target_list, X, Y,
                                                                    PotentialType.Attractive_potential,
                                                                    constants.BARRIER_TYPE,
                                                                    xi=constants.XI, eta=constants.ETA,
                                                                    rho_0=-1)

    repulsive_potential_field = compute_potential_for_a_given_list(obstacle_list, X, Y,
                                                                   PotentialType.Repulsive_potential,
                                                                   constants.BARRIER_TYPE,
                                                                   xi=constants.XI, eta=constants.ETA, rho_0=None)

    return attractive_potential_field + repulsive_potential_field

def compute_potential_and_potential_gradient(X_potential_field,Y_potential_field,X_vector_field, Y_vector_field,target_list, obstacle_list):
    potential_field = compute_potential(X_potential_field,Y_potential_field,target_list,obstacle_list)
    force_x,force_y = compute_potential_gradient(X_vector_field,Y_vector_field,target_list,obstacle_list)
    return potential_field, force_x, force_y


def convert_target_list_to_potential_field_input(target_list):
    input_list = []
    for target in target_list:
        input_list.append((target.xc, target.yc, constants.COEFF_RADIUS*target.radius))
    return input_list


def plot_repulive_field(Xp, Yp, Xf, Yf, potential_field, force_x, force_y):
    # Plot the surface.
    fig = plt.figure(figsize=(18, 8))
    fig.suptitle('representation of the potential field', fontsize=17, fontweight='bold', y=0.98)
    fig.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')

    ax2 = fig.add_subplot(1, 2, 2)


    potential_field = np.minimum(20000,potential_field)
    surf = ax1.plot_surface(Xp, Yp, potential_field, cmap="hot",
                            linewidth=0, antialiased=False)

    M = np.arctan2(force_x, force_y)

    ax2.quiver(Xf, Yf, force_x, force_y, M, units='x', width=0.05, cmap="hsv")
    #ax2.scatter(Xf[::3, ::3], Yf[::3, ::3], color='b', s=2)

    ax2.axis('equal')
    plt.show()

if __name__ == '__main__':
    """Small exemple to what you can get"""
    # target_list = [(1, 1, .1), (1, 7, .1), (7, 1, .1),(7,7,0.1)]
    target_list = [(3, 4, .3 / 2), (4, 5, .3 / 2), (4, 0, .3 / 2)]
    target_list = []
    target_list = [(4, 4, .3*6),(8, 4, .3*6)]
    objectives_list = [(4, 4, 1)]
    X = np.arange(0, 8, 0.01)
    Y = np.arange(0, 8, 0.01)
    X_potential_field, Y_potential_field = np.meshgrid(X, Y)
    X = np.arange(0, 8, 0.5)
    Y = np.arange(0, 8, 0.5)
    X_vector_field, Y_vector_field = np.meshgrid(X, Y)
    potential_field, force_x, force_y = compute_potential_and_potential_gradient(X_potential_field,Y_potential_field,X_vector_field, Y_vector_field,objectives_list,target_list)
    plot_repulive_field(X_potential_field, Y_potential_field, X_vector_field, Y_vector_field, potential_field, force_x, force_y)
