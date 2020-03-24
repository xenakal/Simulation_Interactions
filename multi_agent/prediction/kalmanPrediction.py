from constants import NUMBER_PREDICTIONS, TIME_PICTURE, STD_MEASURMENT_ERROR, TIME_SEND_READ_MESSAGE
from filterpy.kalman import KalmanFilter, update, predict
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag
import numpy as np

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

    def __init__(self, target_id, x_init, y_init):
        # Kalman Filter object
        self.filter = kfObject(x_init, y_init)
        self.target_id = target_id
        self.kalman_memory = []

    def batch_filter_debug(self):
        debug_tracker = kfObject(self.kalman_memory[0][0], self.kalman_memory[0][1])
        means, stds, _, _ = debug_tracker.batch_filter(self.kalman_memory)
        return debug_tracker.rts_smoother(means, stds)[0]

    def add_measurement(self, z):
        self.kalman_memory.append(z)
        self.filter.predict()
        self.filter.update(np.array(z))

        if self.pivot_point_detected():
            print("pivot")
            avg_speeds = avgSpeedFunc(self.kalman_memory[-2:])
            self.filter = kfObject(z[0], z[1], avg_speeds[0], avg_speeds[1])
            self.kalman_memory = [z]

    def pivot_point_detected(self):
        if len(self.kalman_memory) < 10:
            return False

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
        for _ in range(NUMBER_PREDICTIONS):
            new_state, new_P = predict(current_state, current_P, self.filter.F, self.filter.Q)
            predictions.append(new_state[0:2])
            current_state, current_P = update(current_state, current_P, new_state[0:2], self.filter.R, self.filter.H)

        return predictions

    def get_current_position(self):
        return self.filter.x

    def reset_filter(self, x_init, y_init):
        self.filter = kfObject(x_init, y_init)


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


def avgSpeedFunc(positions, timestep=TIME_SEND_READ_MESSAGE+TIME_PICTURE):
    if len(positions) <= 1:  # one position or less not enough to calculate speed
        return 0
    prevPos = positions[0]

    avgSpeed_x = 0.0
    avgSpeed_y = 0.0
    for curPos in positions[1:]:
        stepDistance_x = curPos[0] - prevPos[0]
        stepDistance_y = curPos[1] - prevPos[1]

        avgSpeed_x += stepDistance_x / timestep
        avgSpeed_y += stepDistance_y / timestep

        prevPos = curPos

    avgSpeed_x = avgSpeed_x / (len(positions) - 1)
    avgSpeed_y = avgSpeed_y / (len(positions) - 1)

    return [avgSpeed_x, avgSpeed_y]
