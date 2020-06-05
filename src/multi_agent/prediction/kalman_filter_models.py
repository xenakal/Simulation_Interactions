from src.constants import DISTRIBUTED_KALMAN, KALMAN_MODEL_MEASUREMENT_DIM, TIME_SEND_READ_MESSAGE, TIME_PICTURE, \
    STD_MEASURMENT_ERROR_ACCCELERATION, STD_MEASURMENT_ERROR_SPEED, STD_MEASURMENT_ERROR_POSITION
import src.constants as constants
from warnings import warn
from filterpy.kalman import KalmanFilter
from src.multi_agent.prediction.distributed_kalman_filter import DistributedKalmanFilter
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag
import numpy as np


class KalmanFilterModel:
    """
    Class to represent the model used for the Kalman Filter. There are different possibilities:
        1) measurement dimention = 2 --> x, y positions
        2) measurement dimention = 4 --> x, y positions and velocities
        3) measurement dimention = 6 --> x, y positions, velocities and acceleration
        4) measurement dimention = 2 but output dimention = 4 --> x, y positions and x, y velocities calculated by
           filter as well
    For each of these, the filter can be distributed, or not.

    In order to not mess up the consistency when creating the models at different locations in the src, the measurement
    dimention and the distributed/centralized version are chosen automatically from the corresponding variables found in
    constants.py.
    """

    def __init__(self, x_init, y_init, kalman_logger, vx_init=0, vy_init=0, ax_init=0, ay_init=0, calc_speed=False):
        self.kalman_logger = kalman_logger
        self.filter = self.find_appropriate_filter(x_init, y_init, vx_init, vy_init, ax_init, ay_init, calc_speed)

    def reset_filter(self, x_init, y_init, vx_init=0, vy_init=0, ax_init=0, ay_init=0, calc_speed=False):
        self.filter = self.find_appropriate_filter(x_init, y_init, vx_init, vy_init, ax_init, ay_init, calc_speed)
        return self.filter

    def find_appropriate_filter(self, x_init, y_init, vx_init, vy_init, ax_init, ay_init, calc_speed):
        if KALMAN_MODEL_MEASUREMENT_DIM == 2:
            if calc_speed:
                ret_filter = self.kalman_filter_position_calc_speed(x_init, y_init, vx_init, vy_init)
            else:
                ret_filter = self.kalman_filter_position(x_init, y_init)
        elif KALMAN_MODEL_MEASUREMENT_DIM == 4:
            ret_filter = self.kalman_filter_velocity(x_init, y_init, vx_init, vy_init)
        elif KALMAN_MODEL_MEASUREMENT_DIM == 6:
            ret_filter = self.kalman_filter_acceleration(x_init, y_init, vx_init, vy_init, ax_init, ay_init)
        else:
            warn("There is no implemented model for the specified input size (constants.py), default "
                 "of dim 4 will be used.")
            ret_filter = self.kalman_filter_velocity(x_init, y_init, vx_init, vy_init)

        return ret_filter

    def model_F(self, dt):
        pass

    def kalman_filter_position(self, x_init, y_init):
        """
        :description
            Returns a KalmanFilter object with the model corresponding to our problem.
        :param
            1. (int) x_init     -- initial x coordinate of tracked object
            2. (int) y_init     -- initial y coordinate of tracked object

        :return
            The Kalman Filter object (from pyKalman library) with the model corresponding to our scenario.
        """

        def F_func(dt_arg=TIME_SEND_READ_MESSAGE + TIME_PICTURE):
            return np.array([[1., 0.],
                             [0., 1.]])

        self.model_F = F_func  # !! Carefull with pycharm warning: this is actually the method model F, not an attribute

        f = DistributedKalmanFilter(dim_x=2, dim_z=2, model_F=F_func, logger=self.kalman_logger)

        # initial guess on state variables (velocity initiated to 0 arbitrarily => high )
        f.x = np.array([x_init, y_init])

        # transition matrix
        f.F = F_func()

        f.u = 0
        f.H = np.array([[1., 0.],
                        [0., 1.]])
        f.P *= 2.
        f.R = np.eye(2) * constants.KALMAN_VAR_COEFFICIENT * STD_MEASURMENT_ERROR_POSITION ** 2
        f.B = 0

        dt = TIME_PICTURE + TIME_SEND_READ_MESSAGE
        q = Q_discrete_white_noise(dim=2, dt=dt, var=0.1)  # var => how precise the model is
        f.Q = q  # block_diag(q, q)
        return f

    def kalman_filter_velocity(self, x_init, y_init, vx_init, vy_init):
        """
        :description
            Returns a KalmanFilter object with the model corresponding to our problem.
        :param
            1. (int) x_init     -- initial x coordinate of tracked object
            2. (int) y_init     -- initial y coordinate of tracked object

        :return
            The Kalman Filter object (from pyKalman library) with the model corresponding to our scenario.
        """
        # redifining the model_F function so that we can get F(dt) (ie, transfer matrix evaluated at some delta time)
        # without having to hard src it anywhere else that in this class.
        # This way, we never actually have to touch it again.
        def F_func(dt_arg=TIME_SEND_READ_MESSAGE + TIME_PICTURE):
            return np.array([[1., 0., dt_arg, 0.],
                             [0., 1., 0., dt_arg],
                             [0., 0., 1., 0.],
                             [0., 0., 0., 1.]])

        self.model_F = F_func  # !! Carefull with pycharm warning: this is actually the method model F, not an attribute

        f = DistributedKalmanFilter(dim_x=4, dim_z=4, model_F=F_func, logger=self.kalman_logger)

        # initial guess on state variables (velocity initiated to 0 arbitrarily => high )
        dt = TIME_SEND_READ_MESSAGE + TIME_PICTURE
        f.x = np.array([x_init, y_init, vx_init, vy_init])

        # define transition matrix
        f.F = F_func()

        f.u = 0
        f.H = np.array([[1., 0., 0., 0.],
                        [0., 1., 0., 0.],
                        [0., 0., 1., 0.],
                        [0., 0., 0., 1.]])
        f.P *= 200.
        v_error_p = STD_MEASURMENT_ERROR_POSITION
        v_error_v = STD_MEASURMENT_ERROR_SPEED

        f.R = np.array([[constants.KALMAN_VAR_COEFFICIENT * v_error_p, 0., 0., 0.],
                        [0., constants.KALMAN_VAR_COEFFICIENT * v_error_p, 0., 0.],
                        [0., 0., constants.KALMAN_VAR_COEFFICIENT * v_error_v, 0.],
                        [0., 0., 0., constants.KALMAN_VAR_COEFFICIENT * v_error_v]])

        f.B = np.array([0, 0, 1, 1])
        q = Q_discrete_white_noise(dim=2, dt=dt, var=0.00001)  # var => how precise the model is
        f.Q = block_diag(q, q)
        f.Q *= 0
        return f

    def kalman_filter_acceleration(self, x_init, y_init, vx_init, vy_init, ax_init, ay_init):
        """
        :description
            Returns a KalmanFilter object with the model corresponding to our problem.
        :param
            1. (int) x_init     -- initial x coordinate of tracked object
            2. (int) y_init     -- initial y coordinate of tracked object

        :return
            The Kalman Filter object (from pyKalman library) with the model corresponding to our scenario.
        """

        def F_func(dt=TIME_SEND_READ_MESSAGE + TIME_PICTURE):
            return np.array([[1., 0., dt, 0., 0., 0.],
                             [0., 1., 0., dt, 0., 0.],
                             [0., 0., 1., 0., dt, 0.],
                             [0., 0., 0., 1., 0., dt],
                             [0., 0., 0., 0., 1., 0.],
                             [0., 0., 0., 0., 0., 1.]])

        self.model_F = F_func  # !! Carefull with pycharm warning: this is actually the method model F, not an attribute

        f = DistributedKalmanFilter(dim_x=6, dim_z=6, model_F=F_func, logger=self.kalman_logger)

        # initial guess on state variables (velocity initiated to 0 arbitrarily => high )
        dt = TIME_SEND_READ_MESSAGE + TIME_PICTURE
        f.x = np.array([x_init, y_init, vx_init, vy_init, ax_init, ay_init])
        f.F = F_func()

        f.u = 0
        f.H = np.eye(6, 6)
        f.P *= 2.
        v_error_p = STD_MEASURMENT_ERROR_POSITION ** 2
        v_error_v = STD_MEASURMENT_ERROR_SPEED ** 2
        v_error_a = STD_MEASURMENT_ERROR_ACCCELERATION ** 2

        f.R = np.array([[constants.KALMAN_VAR_COEFFICIENT * v_error_p, 0., 0., 0., 0., 0.],
                        [0., constants.KALMAN_VAR_COEFFICIENT * v_error_p, 0., 0., 0., 0.],
                        [0., 0., constants.KALMAN_VAR_COEFFICIENT * v_error_v, 0., 0., 0.],
                        [0., 0., 0., constants.KALMAN_VAR_COEFFICIENT * v_error_v, 0., 0.],
                        [0., 0., 0., 0., constants.KALMAN_VAR_COEFFICIENT * v_error_a, 0.],
                        [0., 0., 0., 0., 0., constants.KALMAN_VAR_COEFFICIENT * v_error_a]])

        f.B = np.array([0, 0, 0, 0, 0., 0.])
        q = Q_discrete_white_noise(dim=3, dt=dt, var=0.00000001)  # var => how precise the model is
        f.Q = block_diag(q, q)
        return f

    def kalman_filter_position_calc_speed(self, x_init, y_init, vx_init, vy_init):
        """
        :description
            Returns a KalmanFilter object with the model corresponding to our problem.
        :param
            1. (int) x_init     -- initial x coordinate of tracked object
            2. (int) y_init     -- initial y coordinate of tracked object

        :return
            The Kalman Filter object (from pyKalman library) with the model corresponding to our scenario.
        """

        # redifining the model_F function so that we can get F(dt) (ie, transfer matrix evaluated at some delta time)
        # without having to hard src it anywhere else that in this class.
        # This way, we never actually have to touch it again.
        def F_func(dt_arg=TIME_SEND_READ_MESSAGE + TIME_PICTURE):
            return np.array([[1., 0., dt_arg, 0.],
                             [0., 1., 0., dt_arg],
                             [0., 0., 1., 0.],
                             [0., 0., 0., 1.]])

        self.model_F = F_func  # !! Carefull with pycharm warning: this is actually the method model F, not an attribute

        # we have a 4d state space and measurements on only the positions (x,y)
        f = DistributedKalmanFilter(dim_x=4, dim_z=2, model_F=F_func, logger=self.kalman_logger)

        # initial guess on state variables (velocity initiated to 0 arbitrarily => high )
        f.x = np.array([x_init, y_init, vx_init, vy_init])

        # define transition matrix
        f.F = F_func()

        f.u = 0
        f.H = np.array([[1., 0., 0., 0.],
                        [0., 1., 0., 0.]])
        f.P *= 2.
        f.R = np.eye(2) * constants.KALMAN_VAR_COEFFICIENT * STD_MEASURMENT_ERROR_POSITION ** 2
        f.B = 0

        dt = TIME_SEND_READ_MESSAGE + TIME_PICTURE
        q = Q_discrete_white_noise(dim=2, dt=dt, var=0.00000001)  # var => how precise the model is
        f.Q = block_diag(q, q)
        return f
