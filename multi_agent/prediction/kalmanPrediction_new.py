from constants import NUMBER_PREDICTIONS, TIME_PICTURE, STD_MEASURMENT_ERROR_ACCCELERATION,STD_MEASURMENT_ERROR_SPEED,STD_MEASURMENT_ERROR_POSITION, TIME_SEND_READ_MESSAGE
from filterpy.kalman import KalmanFilter, update, predict
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag
import numpy as np
import time

SPEED_CHANGE_THRESHOLD = 4
MAX_STD_SPEED = 0.7


class KalmanPrediction:
    """
        :description
            Wrapper class using FilterPy to compute the Kalman predictions from the noisy positions
            recorded by the agents.
            The class can be used to Smoothen the results or to make Predictions on future positions.

        :param
            1. (int)   target_id  -- identification number of the target
            2. (float) x_init     -- initial x-axis position of object being tracked
            3. (float) y_init     -- initial y-axis position of object being tracked
    """

    def __init__(self, target_id, x_init, y_init, vx_init, vy_init,ax_init,ay_init, timestamp):
        # Kalman Filter object
        self.filter = kfObject3(x_init, y_init, vx_init, vy_init, ax_init, ay_init)
        self.target_id = target_id
        self.kalman_memory = [[x_init, y_init,vx_init,vy_init,ax_init,ay_init, timestamp]]

    def add_measurement_position(self, z, timestamp):
        kalman_memory_element = z.copy()
        kalman_memory_element.append(timestamp)
        last_z = self.kalman_memory[-1]
        self.kalman_memory.append(kalman_memory_element)

        delta_speed_x = z[2]-last_z[2]
        delta_speed_y = z[3]-last_z[3]
        u = np.array([0., 0., delta_speed_x, delta_speed_y])
        B = np.array([0., 0., 1., 1.])
        self.filter.predict(u=u, B=B)
        z = [kalman_memory_element[0],kalman_memory_element[1],kalman_memory_element[2],kalman_memory_element[3]]
        self.filter.update(np.array(z))

    def add_measurement_acceleration_speed_position(self, z, timestamp):
        kalman_memory_element = z.copy()
        kalman_memory_element.append(timestamp)
        last_z = self.kalman_memory[-1]
        self.kalman_memory.append(kalman_memory_element)

        delta_ac_x = 0
        delta_ac_y = 0

        if not z[4] < 0.1 :
            delta_ac_x = z[4]
        if not z[5] == 0:
            delta_ac_y = z[5]


        u = np.array([0., 0., 0., 0., delta_ac_x, delta_ac_y])
        #TODO assez difficile de trouver de bon coefficient
        B = np.array([0., 0., 0., 0., 0.05, 0.05])
        self.filter.predict(u=u, B=B)
        z = [kalman_memory_element[0],kalman_memory_element[1],kalman_memory_element[2],kalman_memory_element[3],kalman_memory_element[4],kalman_memory_element[5]]
        self.filter.update(np.array(z))


    def pivot_point_detected(self):
        if self.kalman_memory[-1][4] > STD_MEASURMENT_ERROR_ACCCELERATION + 0.5 or self.kalman_memory[-1][5] > STD_MEASURMENT_ERROR_ACCCELERATION + 0.5:
            return True



def kfObject_speed_position(x_init, y_init, vx_init=0.0, vy_init=0.0,ax_init = 0.0,ay_init = 0.0):
    """
    :description
        Returns a KalmanFilter object with the model corresponding to our problem.
    :param
        1. (int) x_init     -- initial x coordinate of tracked object
        2. (int) y_init     -- initial y coordinate of tracked object

    :return
        The Kalman Filter object (from pyKalman library) with the model corresponding to our scenario.
    """

    f = KalmanFilter(dim_x=4,
                     dim_z=4)  # as we have a 4d state space and measurements on only the positions (x,y)
    # initial guess on state variables (velocity initiated to 0 arbitrarily => high )
    dt = TIME_SEND_READ_MESSAGE + TIME_PICTURE
    f.x = np.array([x_init, y_init, vx_init, vy_init])
    f.F = np.array([[1., 0., dt, 0.],
                    [0., 1., 0., dt],
                    [0., 0., 1., 0.],
                    [0., 0., 0., 1.]])
    f.u = 0
    f.H = np.array([[1., 0., 0., 0.],
                    [0., 1., 0., 0.],
                    [0., 0., 1., 0.],
                    [0., 0., 0., 1.]])
    f.P *= 2.
    v_error_p = STD_MEASURMENT_ERROR_POSITION**2
    v_error_v = STD_MEASURMENT_ERROR_SPEED** 2

    f.R = np.array([[v_error_p, 0., 0., 0.],
                    [0., v_error_p, 0., 0.],
                    [0., 0., v_error_v, 0.],
                    [0., 0., 0., v_error_v]])

    f.B = np.array([0, 0, 1, 1])
    q = Q_discrete_white_noise(dim=2, dt=dt, var=0.1)  # var => how precise the model is
    f.Q = block_diag(q, q)
    return f

def kfObject_acceleration_speed_position(x_init, y_init, vx_init=0.0, vy_init=0.0, ax_init = 0.0,ay_init = 0.0):
    """
    :description
        Returns a KalmanFilter object with the model corresponding to our problem.
    :param
        1. (int) x_init     -- initial x coordinate of tracked object
        2. (int) y_init     -- initial y coordinate of tracked object

    :return
        The Kalman Filter object (from pyKalman library) with the model corresponding to our scenario.
    """

    f = KalmanFilter(dim_x=6,
                     dim_z=6)  # as we have a 4d state space and measurements on only the positions (x,y)

    # initial guess on state variables (velocity initiated to 0 arbitrarily => high )
    dt = TIME_SEND_READ_MESSAGE + TIME_PICTURE
    f.x = np.array([x_init, y_init, vx_init, vy_init,ax_init,ay_init])
    f.F = np.array([[1., 0., dt, 0., 0., 0.],
                    [0., 1., 0., dt, 0., 0.],
                    [0., 0., 1., 0., dt, 0.],
                    [0., 0., 0., 1., 0., dt],
                    [0., 0., 0., 0., 1., 0.],
                    [0., 0., 0., 0., 0., 1.]])
    f.u = 0
    f.H = np.eye(6,6)
    f.P *= 2.
    v_error_p = STD_MEASURMENT_ERROR_POSITION**2
    v_error_v = STD_MEASURMENT_ERROR_SPEED** 2
    v_error_a =  STD_MEASURMENT_ERROR_ACCCELERATION** 2

    f.R = np.array([[v_error_p, 0., 0., 0., 0., 0.],
                    [0., v_error_p, 0., 0., 0., 0.],
                    [0., 0., v_error_v, 0., 0., 0.],
                    [0., 0., 0., v_error_v, 0., 0.],
                    [0., 0., 0., 0., v_error_a, 0.],
                    [0., 0., 0., 0., 0., v_error_a]])

    f.B = np.array([0, 0, 0, 0, 0., 0.])
    q = Q_discrete_white_noise(dim=3, dt=dt, var=0.1)  # var => how precise the model is
    f.Q = block_diag(q, q)
    return f


