from constants import NUMBER_PREDICTIONS, TIME_PICTURE, STD_MEASURMENT_ERROR, TIME_SEND_READ_MESSAGE
from filterpy.kalman import KalmanFilter, update, predict
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag
import numpy as np
import math

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

    def __init__(self, target_id, x_init, y_init, timestamp):
        # Kalman Filter object
        self.filter = kfObject(x_init, y_init)
        self.target_id = target_id
        self.kalman_memory = [[x_init, y_init, timestamp]]
        self.number_of_pivots = 0  # for debug
        self.data_collected = 0

    def add_measurement(self, z, timestamp):
        self.data_collected += 1
        kalman_memory_element = z.copy()
        kalman_memory_element.append(timestamp)
        self.kalman_memory.append(kalman_memory_element)

        if self.pivot_point_detected():
            self.number_of_pivots += 1
            print("pivot = ", self.number_of_pivots)
            avg_speeds = avgSpeedFunc(self.kalman_memory[-2:], self.data_collected)
            self.reset_filter(z[0], z[1], avg_speeds[0], avg_speeds[1])
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
        self.filter.update(np.array(z))

    def pivot_point_detected(self):
        """
        :description
            Detects a pivot point (ie a point where the trajectory changes) by checking if the speed in either axis
            change.
        :return:
            True if a pivot point is detected, False otherwise.
        :notes:
            We could calculate the differences in times of adjacent positions (ie last.time - previous.time) and
            find the covarience in these differences to calculate the threshold used.
        """
        if len(self.kalman_memory) < 10:
            return False
        """
        avg_speed = avgSpeedFunc(self.kalman_memory[:-2], self.data_collected)           # avg speed up to now
        #print("avg_speed = ", avg_speed)
        last_speed = avgSpeedFunc(self.kalman_memory[-2:], self.data_collected)          # last speed
        #print("last_speed= ", last_speed)
        speed_diff_x = math.fabs(avg_speed[0] - last_speed[0])
        speed_diff_y = math.fabs(avg_speed[1] - last_speed[1])

        return speed_diff_x > SPEED_CHANGE_THRESHOLD or speed_diff_y > SPEED_CHANGE_THRESHOLD
        """

        x = [_[0] for _ in self.kalman_memory]
        y = [_[1] for _ in self.kalman_memory]
        x_std = np.std(x)
        y_std = np.std(y)

        return x_std > MAX_STD_SPEED or y_std > MAX_STD_SPEED

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
        self.filter = kfObject(x_init, y_init, vx_init, vy_init)


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

    f = KalmanFilter(dim_x=4,
                     dim_z=2)  # as we have a 4d state space and measurements on only the positions (x,y)
    # initial guess on state variables (velocity initiated to 0 arbitrarily => high )
    dt = TIME_SEND_READ_MESSAGE + TIME_PICTURE
    f.x = np.array([x_init, y_init, vx_init, vy_init])
    f.F = np.array([[1., 0., dt, 0.],
                    [0., 1., 0., dt],
                    [0., 0., 1., 0.],
                    [0., 0., 0., 1.]])
    f.u = 0
    f.H = np.array([[1., 0., 0., 0.],
                    [0., 1., 0., 0.]])
    f.P *= 2.
    f.R = np.eye(2) * STD_MEASURMENT_ERROR**2
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
    f.R = np.eye(4) * STD_MEASURMENT_ERROR**2
    v_error = STD_MEASURMENT_ERROR**2
    f.R = np.array([[v_error, 0., 0., 0.],
                    [0., v_error, 0., 0.],
                    [0., 0., 2*v_error, 0.],
                    [0., 0., 0., 2*v_error]])
    f.B = np.array([0, 0, 1, 1])
    q = Q_discrete_white_noise(dim=2, dt=dt, var=0.1)  # var => how precise the model is
    f.Q = block_diag(q, q)
    return f


def avgSpeedFunc(positions, data_collected):
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
        #timestep = curPos[2] - prevTime

        avgSpeed_x += stepDistance_x / timestep
        avgSpeed_y += stepDistance_y / timestep

        prevPos_x = curPos[0]
        prevPos_y = curPos[1]
        prevTime = curPos[2]

    avgSpeed_x = avgSpeed_x / (len(positions) - 1)
    avgSpeed_y = avgSpeed_y / (len(positions) - 1)
    if avgSpeed_y > 1 or avgSpeed_x > 1:
        print(data_collected)
    print(avgSpeed_x, avgSpeed_y)

    return [avgSpeed_x, avgSpeed_y]
