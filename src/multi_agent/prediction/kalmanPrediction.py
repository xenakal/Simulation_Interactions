from src.constants import NUMBER_PREDICTIONS, STD_MEASURMENT_ERROR_SPEED, STD_MEASURMENT_ERROR_ACCCELERATION, KALMAN_MODEL_MEASUREMENT_DIM
import src.constants as constants
from filterpy.kalman import update, predict
import numpy as np
import warnings
from src.multi_agent.prediction.kalman_filter_models import KalmanFilterModel
import src.my_utils.my_IO.IO_data as log

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
        # logger to gather debug information
        self.logger_kalman = log.create_logger(constants.ResultsPath.LOG_KALMAN, "kalman_info_" + str(target_id),
                                               agent_id)
        # contains the information on the model used
        self.filter_model = KalmanFilterModel(x_init, y_init, self.logger_kalman, vx_init, vy_init, ax_init, ay_init,
                                              calc_speed=True)
        # actual filter that processes the measurements
        self.filter = self.filter_model.filter
        # id of tracked target
        self.target_id = target_id
        # agent making the measurements
        self.agent_id = agent_id
        # information stored
        kalman_memory_element = [x_init, y_init, vx_init, vy_init, ax_init, ay_init, timestamp]
        # list to store the information
        self.kalman_memory = [kalman_memory_element]
        # timestamp of last measurement received
        self.prev_timestamp = timestamp

    def add_measurement(self, z, timestamp):
        """
        :description
            Adds a measurement to the filter and performs a predict() and update() step based on this new info.

        :param
            z: [x, y, vx, vy, ax, ay]  -- list of the different measurements
            timestamp: int             -- time at which the measurements was made
        """
        # information stored
        kalman_memory_element = z.copy()
        # also add the timestamp
        kalman_memory_element.append(timestamp)
        self.kalman_memory.append(kalman_memory_element)

        pivot_detected = False
        # a pivot is defined as a change of direction (in our case equivalent to change in speed in either axis)
        if self.pivot_point_detected_speed():
            # filter reset to "forget" the previous information
            self.reset_filter(*z)
            # memory reset as well
            self.kalman_memory = [kalman_memory_element]
            pivot_detected = True

        dt = timestamp - self.prev_timestamp
        self.prev_timestamp = timestamp
        F = self.filter_model.model_F(dt)
        self.filter.predict(F=F)

        if constants.DISTRIBUTED_KALMAN:
            self.filter.update(np.array(z[:KALMAN_MODEL_MEASUREMENT_DIM]), timestamp=timestamp)
        else:
            self.filter.update(np.array(z[:KALMAN_MODEL_MEASUREMENT_DIM]))

        return pivot_detected

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
        try:
            for _ in range(NUMBER_PREDICTIONS):
                new_state, new_P = predict(current_state, current_P, self.filter_model.model_F(dt), self.filter.Q)
                predictions.append((new_state, new_P))
                current_state, current_P = update(new_state, new_P, new_state[0:KALMAN_MODEL_MEASUREMENT_DIM],
                                                  self.filter.R, self.filter.H)
        except ValueError:
            print("error in prediction")
            import sys
            print(sys.exc_info())
            print("current_state: ", current_state)

        return predictions

    def get_current_position(self):
        return self.filter.x, self.filter.P

    def reset_filter(self, x_init, y_init, vx_init, vy_init, ax_init, ay_init):
        self.filter = self.filter_model.reset_filter(x_init, y_init, vx_init, vy_init, ax_init, ay_init, calc_speed=True)

    def get_DKF_info_string(self):
        if constants.DATA_TO_SEND != "dkf":
            warnings.warn("sending state/var error info even though DKF not defined in constants")
        return self.filter.get_DKF_info_string()

    def assimilate(self, dkf_info_string, timestamp):
        if constants.DATA_TO_SEND != "dkf":
            warnings.warn("assimilating data even though DKF not defined in constants")
        if constants.USE_TIMESTAMP_FOR_ASSIMILATION:
            self.filter.assimilate(dkf_info_string, timestamp)
        else:
            self.filter.assimilate(dkf_info_string, constants.get_time())
