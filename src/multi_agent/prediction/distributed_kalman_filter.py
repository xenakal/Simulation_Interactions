from filterpy.kalman import KalmanFilter
import numpy as np
from numpy import eye, dot, zeros, isscalar
from filterpy.common import reshape_z
from src.constants import TIME_SEND_READ_MESSAGE, TIME_PICTURE, STD_MEASURMENT_ERROR_POSITION
import src.constants as constants
import warnings

DEFAULT_TIME_INCREMENT = TIME_PICTURE + TIME_SEND_READ_MESSAGE
INTERNODAL_VALIDATION_BOUND = 2


class DistributedKalmanFilter(KalmanFilter):
    """
    Extends the KalmanFilter class from the filterPy library. It implements a distributed Kalman Filter.
    It also adapts the class from filterPy such that it uses the information form of the variance.
    The class is used to implement the DKF such as described in this paper:
          Rao, B. S. Y., Durrant-Whyte, H. F., & Sheen, J. A. (1993).
          A Fully Decentralized Multi-Sensor System For Tracking and Surveillance.
          The International Journal of Robotics Research, 12(1), 20–44. https://doi.org/10.1177/027836499301200102
    """

    def __init__(self, dim_x, dim_z, logger, dt=DEFAULT_TIME_INCREMENT, dim_u=0, model_F=None):

        super().__init__(dim_x, dim_z, dim_u)

        # values used for information form of Kalman equations
        self.PI = eye(dim_x)  # inverse of P (used for information form of KF)
        self.PI_prior = eye(dim_x)  # copy of PI after predict() is called
        self.PI_post = eye(dim_x)  # copy of PI afer update() is called
        self.W = zeros((dim_x, dim_z))  # Kalman gain
        self.x_global = zeros((dim_x, 1))  # global estimate of target state
        self.P_global = eye(dim_x)  # global estimate of covariance matrix
        self.PI_global = eye(dim_x)  # inverse of global estimate P
        self.curr_ti = -1  # timestamp of current measurement
        self.dt = dt  # time difference between measurements
        self.prev_ti = -1  # time of previous measurement
        self.z_current = None  # last measurement
        if model_F is None:
            def default_F(dt_arg):
                return np.array([[1., 0., dt_arg, 0.],
                                 [0., 1., 0., dt_arg],
                                 [0., 0., 1., 0.],
                                 [0., 0., 0., 1.]])
            self.model_F = default_F  # default if nothing is given
        else:
            self.model_F = model_F  # function to get the transition matrix ( use: F = self.model_F(dt) )

        # creation of log file
        #self.logger_kalman = log.create_logger(constants.ResultsPath.LOG_KALMAN, "kalman_info_" + str(target_id), agent_id)
        self.logger_kalman = logger
        self.logger_kalman.info("new distributed kalman at time %.02f s" % constants.get_time())

    def predict(self, u=None, B=None, F=None, Q=None):
        super().predict(u, B, F, Q)
        self.PI = self.inv(self.P)
        self.PI_prior = self.PI.copy()

    def update(self, z, R=None, H=None, timestamp=-1):

        if timestamp == -1:
            warnings.warn("timestamp not specified: default time increment will be used")

            # timestep set to last time difference between subsequent measurements
            self.dt = DEFAULT_TIME_INCREMENT
            self.prev_ti = self.curr_ti
            self.curr_ti += DEFAULT_TIME_INCREMENT

        else:
            # timestep set to last time difference between subsequent measurements
            self.prev_ti = self.curr_ti
            self.curr_ti = timestamp
            self.dt = timestamp - self.curr_ti

        # set to None to force recompute
        self._log_likelihood = None
        self._likelihood = None
        self._mahalanobis = None

        if z is None:
            self.z = np.array([[None] * self.dim_z]).T
            self.x_post = self.x.copy()
            self.P_post = self.P.copy()
            self.y = zeros((self.dim_z, 1))
            return

        z = reshape_z(z, self.dim_z, self.x.ndim)
        self.z_current = z

        if R is None:
            R = self.R
        elif isscalar(R):
            R = eye(self.dim_z) * R

        if H is None:
            H = self.H

        # y = z - Hx
        # error (residual) between measurement and prediction
        self.y = z - dot(H, self.x)

        # inverse of R, used in information form of variance update and Kalman gain
        RI = self.inv(R)

        # information form of variance update equation
        # PI = PI + HT*RI*H
        self.PI = self.PI + dot(dot(H.T, RI), H)
        self.PI_post = self.PI.copy()

        # needed for Kalman gain matrix
        self.P = self.inv(self.PI)

        # Kalman gain matrix
        # W = P*HT*RI
        self.W = dot(dot(self.P, H.T), RI)

        # x = x + Wy
        self.x = self.x + dot(self.W, self.y)

        # update x_post & P_post
        self.x_post = self.x
        self.P_post = self.P

    def assimilate(self, dkf_info_string, tj):
        """
        Assimilates the local estimation recieved from another node to the local estimation of the global state.

        :param (dkf_info_string) dkf_info_string     -- string containing the state/variance error info needed for the
                                                        assimilation step
        :param (int) ti                              -- time of arrival of the other arguments to this
                                                        node. In practice, we have to put the time
        """

        if tj < self.curr_ti:
            print("probleeeem")
            return

        [state_error_info, variance_error_info] = parse_errors_info_string(dkf_info_string)

        delta_t = tj - self.prev_ti  # δt = tj - τi ≃ ti - τi

        ## Pj_prior: PI(tj|τi) = F(δt)*P(τi|τi)FT(δt) + Q
        Pj_prior = dot(dot(self.model_F(delta_t), self.P_post), self.model_F(delta_t).T) + self.Q
        PIj_prior = self.inv(Pj_prior)

        ## xj_prior: x(tj|τi) = F(δt)x(τi|τi)
        xj_prior = dot(self.model_F(delta_t), self.x_post)

        # Internodal Validation
        Y_minus = dot(self.H.T, dot(self.inv(dot(self.H, dot(variance_error_info, self.H.T))), self.H))
        Nij_subexpression = self.inv(dot(self.H, dot(variance_error_info, self.H.T))) + dot(self.H, dot(self.P_post,
                                                                                                        self.H.T))
        Nij = dot(self.H.T, dot(Nij_subexpression, self.H))
        Hij = dot(Y_minus, state_error_info) - dot(self.H.T, dot(self.H, xj_prior))
        region_to_validate = dot(Hij.transpose(), dot(self.inv(Nij), Hij))
        if region_to_validate < INTERNODAL_VALIDATION_BOUND:
            return
        else:
            self.logger_kalman.info("Assimilation of data at time " + str(constants.get_time()) + ". Time when data "
                                                                                                  "was sent: " +
                                    str(tj) + ". Time of last local measurement: " + str(self.curr_ti))

        # PI(tj|tj) = PI(tj|τi) + variance_error_info
        self.PI_global = PIj_prior + variance_error_info
        self.P_global = self.inv(self.PI_global)

        # x(tj|tj) = P(tj|tj)[PI(tj|τi)x(tj|τi) + state_error_info]
        x_global_part1 = dot(PIj_prior, xj_prior)
        x_global_part2 = x_global_part1 + state_error_info
        self.x_global = dot(self.P_global, x_global_part2)

        # udpate the state and covariance
        self.x = self.x_global.copy()
        self.PI = self.PI_global.copy()
        self.P = self.P_global.copy()

        self.prev_ti = self.curr_ti
        self.curr_ti = tj

    def state_error_info(self):
        RI = self.inv(self.R)
        HRI = dot(self.H.T, RI)
        state_error_info = dot(HRI, self.z_current)
        self.logger_kalman.info("Calc state_error_info = " + str(state_error_info))
        return state_error_info

    def variance_error_info(self):
        RI = self.inv(self.R)
        var_error_info = dot(dot(self.H.T, RI), self.H)
        self.logger_kalman.info("Calc var_error_info = " + str(var_error_info))
        return var_error_info

    def errors_info_toString(self):
        """
        :description:
            Puts the state_error_info and variance_error_info in a nice string.
        :return: state_error_info / variance_error_info & target_id in a string
        """
        s1 = "StateErrorInfo=" + npArray_to_String(self.state_error_info())
        s2 = "VarianceErrorInfo=" + npArray_to_String(self.variance_error_info())
        return s1 + "%" + s2

    def get_DKF_info_string(self):
        return self.errors_info_toString()


def npArray_to_String(array):
    """
    Converts a np array to a string that can be sent correctly using the mailbox
    :param array: np array
    :return: a string corresponding to this array
    """
    return np.array2string(array).replace(" ", "&").replace("\n", "$")


def npString_to_array(string):
    """
    Converts a string parsed by npArray_to_String back to an np array again.
    :param string: string output of npArray_to_String
    :return: np array corresponding to this String
    """
    formated_string = string.replace("$", "\n").replace("&", " ")
    if formated_string[1] != "[":
        formated_string = formated_string[1:-1]
        rows = formated_string.split("\n")
        return state_error_info_string_to_array(rows[0])
    else:
        formated_string = formated_string[2:-2]
        rows = formated_string.split("\n")
        return var_error_info_string_to_array(rows)


def state_error_info_string_to_array(row):
    row = row.split(" ")
    ret_arr = np.empty(4,)
    index = 0
    for elem in row:
        if elem not in ["", "[", " "]:
            ret_arr[index] = float(elem)
            index += 1
    state_error_info = np.array(ret_arr)
    return state_error_info


def var_error_info_string_to_array(rows):
    ret_arr = np.empty((4, 4))
    row_index = 0
    for row in rows:
        row = row.split(" ")
        column_index = 0
        for elem in row:
            if elem not in ["", "[", " "]:
                if elem[-1] == "]":
                    elem = elem[:-1]
                if elem[0] == "[":
                    elem = elem[1:]
                ret_arr[row_index, column_index] = float(elem)
                column_index += 1
        row_index += 1

    return ret_arr


def parse_errors_info_string(string):
    """
    :description:
        Parses a string as encoded by the errors_info_toString function
    :param string: a string encoded by the errors_info_toString function
    :return: [state_error_info, variance_error_info]
    """
    try:
        [state_error_info_str, var_error_info_str] = string.split("%")
        [_, state_error_info_value] = state_error_info_str.split("=")
        [_, var_error_info_value] = var_error_info_str.split("=")
        state_error_info_value = npString_to_array(state_error_info_value)
        var_error_info_value = npString_to_array(var_error_info_value)
        return state_error_info_value, var_error_info_value
    except ValueError:
        print("error occured during parsing of DKF string")
        print("string to parse: ", string)
        import sys
        print(sys.exc_info())
        exit(1)

