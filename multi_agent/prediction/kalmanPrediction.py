from constants import NUMBER_PREDICTIONS, TIME_PICTURE, STD_MEASURMENT_ERROR_POSITION, TIME_SEND_READ_MESSAGE, \
    STD_MEASURMENT_ERROR_SPEED, STD_MEASURMENT_ERROR_ACCCELERATION, DATA_TO_SEND
from filterpy.kalman import KalmanFilter, update, predict
from filterpy.common import Q_discrete_white_noise
from multi_agent.prediction.distributed_kalman_filter import DistributedKalmanFilter
from scipy.linalg import block_diag
import numpy as np
import warnings
import time
import math

MARGE_SPEED_ERROR = 0.5
SPEED_CHANGE_THRESHOLD = 2 * STD_MEASURMENT_ERROR_SPEED + MARGE_SPEED_ERROR
MARGE_ACC_ERROR = 0.5
ACC_CHANGE_THRESHOLD = STD_MEASURMENT_ERROR_ACCCELERATION + MARGE_ACC_ERROR


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

    def __init__(self, agent_id, target_id, x_init, y_init, vx_init, vy_init, ax_init, ay_init, timestamp):
        # Kalman Filter object
        # TODO: change that to a Factory (this way easily change reset_filter() as well).
        self.filter = distributed_kfObject(x_init, y_init, vx_init, vy_init)
        self.target_id = target_id
        self.agent_id = agent_id
        kalman_memory_element = [x_init, y_init, vx_init, vy_init, ax_init, ay_init, timestamp]
        self.kalman_memory = [kalman_memory_element]

    def add_measurement(self, z, timestamp):
        """
        :description
            Adds a measurement to the filter and performs a predict() and update() step based on this new info.

        :param
            z: [x, y, vx, vy, ax, ay]  -- list of the different measurements
            timestamp: int             -- time at which the measurements was made
        """
        kalman_memory_element = z.copy()
        kalman_memory_element.append(timestamp)
        self.kalman_memory.append(kalman_memory_element)

        if self.pivot_point_detected_speed():
            self.reset_filter(z[0], z[1], z[2], z[3])
            self.kalman_memory = [kalman_memory_element]
        """
        avg_speed_old = avgSpeedFunc(self.kalman_memory[-NUMBER_AVERAGE*2-2:-NUMBER_AVERAGE-1])
        avg_speed_new = avgSpeedFunc(self.kalman_memory[-NUMBER_AVERAGE-1:])
        delta_avg_speed_x = avg_speed_new[0] - avg_speed_old[0]
        delta_avg_speed_y = avg_speed_new[1] - avg_speed_old[1]
        #print(round(delta_avg_speed_x))
        #print(round(delta_avg_speed_y))
        print(delta_avg_speed_x)
        print(delta_avg_speed_y)
        u = np.array([0., 0., delta_avg_speed_x, delta_avg_speed_y])
        B = np.array([0., 0., 1., 1.])
        self.filter.predict(u=u, B=B)
        """
        self.filter.predict()
        self.filter.update(np.array([z[0], z[1]]))

    def pivot_point_detected_acc(self):
        acc_x = np.abs(self.kalman_memory[-1][4])
        acc_y = np.abs(self.kalman_memory[-1][5])
        return acc_x > ACC_CHANGE_THRESHOLD or acc_y > ACC_CHANGE_THRESHOLD

    def pivot_point_detected_speed(self):
        """
        :description
            Detects a pivot point (ie a point where the trajectory changes) by checking if the speed in either axis
            changes more than expected.
        :return:
            True if a pivot point is detected, False otherwise.
        """
        if len(self.kalman_memory) < 2:
            return False

        prev_speed_xy = np.array([self.kalman_memory[-2][2], self.kalman_memory[-2][3]])
        current_speed_xy = np.array([self.kalman_memory[-1][2], self.kalman_memory[-1][3]])
        speed_diff = np.abs(prev_speed_xy - current_speed_xy)
        return True in [diff > SPEED_CHANGE_THRESHOLD for diff in speed_diff]

    def get_predictions(self):
        """
        :description
            Starting from the current position, make predictions and propagate using the Kalman transition matrix (defined
            by our model) to make predictions on futur positions.
        :return:
            ([x1, y1], [x2, y2], ...)  predictions     -- a list of size NUMBER_PREDICTIONS containing the
                                                           predicted positions of the target beeing tracked
        """
        predictions = []
        # only return if still seeing the object
        if (not len(self.kalman_memory) < 2) and (self.kalman_memory[-2][2] - self.kalman_memory[-1][2] > 3):
            return predictions

        current_state = self.filter.x
        current_P = self.filter.P
        dt = 0.4
        F = np.array([[1., 0., dt, 0.],
                      [0., 1., 0., dt],
                      [0., 0., 1., 0.],
                      [0., 0., 0., 1.]])
        for _ in range(NUMBER_PREDICTIONS):
            new_state, new_P = predict(current_state, current_P, F, self.filter.Q)
            predictions.append(new_state[0:2])
            predictions.append(new_state)
            current_state, current_P = update(current_state, current_P, new_state[0:2], self.filter.R, self.filter.H)
            # current_state, current_P = update(current_state, current_P, new_state, self.filter.R, self.filter.H)
        return predictions

    def get_current_position(self):
        return self.filter.x

    def reset_filter(self, x_init, y_init, vx_init, vy_init):
        self.filter = distributed_kfObject(x_init, y_init, vx_init, vy_init)

    def get_DKF_info_string(self):
        if DATA_TO_SEND != "dkf":
            warnings.warn("sending state/var error info even though DKF not defined in constants")
        return self.filter.get_DKF_info_string()

    def assimilate(self, dkf_info_string, timestamp):
        if DATA_TO_SEND != "dkf":
            warnings.warn("sending state/var error info even though DKF not defined in constants")
        self.filter.assimilate(dkf_info_string, timestamp)


def distributed_kfObject(x_init, y_init, vx_init, vy_init):
    """
    :description
        Returns a KalmanFilter object with the model corresponding to our problem.
    :param
        1. (int) x_init     -- initial x coordinate of tracked object
        2. (int) y_init     -- initial y coordinate of tracked object

    :return
        The Kalman Filter object (from pyKalman library) with the model corresponding to our scenario.
    """

    # we have a 4d state space and measurements on only the positions (x,y)
    # f = KalmanFilter(dim_x=4, dim_z=2)
    f = DistributedKalmanFilter(dim_x=4, dim_z=2)
    # initial guess on state variables (velocity initiated to 0 arbitrarily => high )
    dt = TIME_SEND_READ_MESSAGE + TIME_PICTURE
    f.x = np.array([x_init, y_init, vx_init, vy_init])

    """
    def F():
    return np.array([[1., 0., f.dt, 0.],
                     [0., 1., 0., f.dt],
                     [0., 0., 1., 0.],
                     [0., 0., 0., 1.]])

    f.model_F = F
    f.model_F()
    """
    f.F = np.array([[1., 0., dt, 0.],
                    [0., 1., 0., dt],
                    [0., 0., 1., 0.],
                    [0., 0., 0., 1.]])

    f.u = 0
    f.H = np.array([[1., 0., 0., 0.],
                    [0., 1., 0., 0.]])
    f.P *= 2.
    f.R = np.eye(2) * STD_MEASURMENT_ERROR_POSITION ** 2
    f.B = 0
    q = Q_discrete_white_noise(dim=2, dt=f.dt, var=0.1)  # var => how precise the model is
    f.Q = block_diag(q, q)
    return f


def kfObject(x_init, y_init, vx_init=0.0, vy_init=0.0):
    """
    :description
        Returns a KalmanFilter object with the model corresponding to our problem.
    :param
        1. (int) x_init     -- initial x coordinate of tracked object
        2. (int) y_init     -- initial y coordinate of tracked object

    :return
        The Kalman Filter object (from pyKalman library) with the model corresponding to our scenario.
    """
    # we have a 4d state space and measurements on only the positions (x,y)
    f = KalmanFilter(dim_x=4, dim_z=2)
    # initial guess on state variables (velocity initiated to 0 arbitrarily => high )
    dt = TIME_SEND_READ_MESSAGE + TIME_PICTURE
    f.x = np.array([x_init, y_init, vx_init, vy_init])

    """
    def F():
        return np.array([[1., 0., f.dt, 0.],
                         [0., 1., 0., f.dt],
                         [0., 0., 1., 0.],
                         [0., 0., 0., 1.]])

    f.model_F = F
    f.model_F()
    """
    f.F = np.array([[1., 0., dt, 0.],
                    [0., 1., 0., dt],
                    [0., 0., 1., 0.],
                    [0., 0., 0., 1.]])

    f.u = 0
    f.H = np.array([[1., 0., 0., 0.],
                    [0., 1., 0., 0.]])
    f.P *= 2.
    f.R = np.eye(2) * STD_MEASURMENT_ERROR_POSITION ** 2
    f.B = 0
    q = Q_discrete_white_noise(dim=2, dt=dt, var=0.1)  # var => how precise the model is
    f.Q = block_diag(q, q)
    return f


def kfObject2(x_init, y_init, vx_init=0.0, vy_init=0.0):
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
    f.R = np.eye(4) * STD_MEASURMENT_ERROR_POSITION ** 2
    v_error = STD_MEASURMENT_ERROR_POSITION ** 2
    f.R = np.array([[v_error, 0., 0., 0.],
                    [0., v_error, 0., 0.],
                    [0., 0., 2 * v_error, 0.],
                    [0., 0., 0., 2 * v_error]])
    f.B = np.array([0, 0, 1, 1])
    q = Q_discrete_white_noise(dim=2, dt=dt, var=0.1)  # var => how precise the model is
    f.Q = block_diag(q, q)
    return f


def avgSpeedFunc(positions):
    """
    :description
        Calculates the average speed of the target based on the positions & times passed in the argument.
    :param
        ([[x, y, timestamp], ...]) positions -- sublist of kalmanPrediction.kalman_memory
    """
    if len(positions) < 2:
        return [0, 0]
    first_position = positions[0]
    prevPos_x = first_position[0]
    prevPos_y = first_position[1]
    prevTime = first_position[2]

    avgSpeed_x = 0.0
    avgSpeed_y = 0.0
    timestep = TIME_SEND_READ_MESSAGE + TIME_PICTURE
    for curPos in positions[1:]:
        stepDistance_x = curPos[0] - prevPos_x
        stepDistance_y = curPos[1] - prevPos_y
        # timestep = curPos[2] - prevTime

        avgSpeed_x += stepDistance_x / timestep
        avgSpeed_y += stepDistance_y / timestep

        prevPos_x = curPos[0]
        prevPos_y = curPos[1]
        prevTime = curPos[2]

    avgSpeed_x = avgSpeed_x / (len(positions) - 1)
    avgSpeed_y = avgSpeed_y / (len(positions) - 1)

    return [avgSpeed_x, avgSpeed_y]
