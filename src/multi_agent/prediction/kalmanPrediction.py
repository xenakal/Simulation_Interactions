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

        self.pivot_point_detected = False

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

        # a pivot is defined as a change of direction (in our case equivalent to change in speed in either axis)
        if self.pivot_point_detected_speed() or self.pivot_point_detected:
            # print("pivot: ", self.agent_id, constants.get_time())
            # filter reset to "forget" the previous information
            self.reset_filter(*z)
            # memory reset as well
            self.kalman_memory = [kalman_memory_element]

        dt = timestamp - self.prev_timestamp
        self.prev_timestamp = timestamp
        F = self.filter_model.model_F(dt)
        self.filter.predict(F=F)

        self.pivot_point_detected = self.filter.update(np.array(z[:KALMAN_MODEL_MEASUREMENT_DIM]), timestamp=timestamp)

    def pivot_point_detected_speed(self):
        """
        :description
            Detects a pivot point (ie a point where the trajectory changes) by checking if the speed in either axis
            changes more than expected.
        :return:
            True if a pivot point is detected, False otherwise.
        """
        return False
        n = 4
        list_to_check = self.kalman_memory
        list_len = len(list_to_check)
        if list_len > n:

            vx = [elem[2] for elem in list_to_check[-1 - n:-1]]
            vy = [elem[3] for elem in list_to_check[-1 - n:-1]]


            vx_std = np.std(vx)
            vy_std = np.std(vy)

            #TODO ici checker pour voir les limites atteignables
            cdt_speed = np.power(np.square(vx_std)+np.square(vy_std),0.5) > 1.5*np.sqrt(2)*constants.STD_MEASURMENT_ERROR_SPEED
            if cdt_speed:
                return True
        return False

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

    def innovation_smaller_than_bound(self):
        return self.filter.innovation_smaller_than_bound()

    def get_current_position(self):
        return self.filter.x, self.filter.P

    def reset_filter(self, x_init, y_init, vx_init, vy_init, ax_init, ay_init):
        self.filter = self.filter_model.reset_filter(x_init, y_init, vx_init, vy_init, ax_init, ay_init, calc_speed=True)

    def get_DKF_info_string(self):
        if constants.DATA_TO_SEND != "dkf":
            warnings.warn("sending state/var error info even though DKF not defined in constants")
        return self.filter.get_DKF_info_string()

    def assimilate(self, dkf_info_string, timestamp):
        if constants.DATA_TO_SEND != constants.AgentCameraCommunicationBehaviour.DKF:
            warnings.warn("assimilating data even though DKF not defined in constants")
        if constants.USE_TIMESTAMP_FOR_ASSIMILATION:
            self.filter.assimilate(dkf_info_string, timestamp)
        else:
            self.filter.assimilate(dkf_info_string, constants.get_time())
