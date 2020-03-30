from filterpy.kalman import KalmanFilter
import numpy as np
from numpy import eye, dot, zeros, isscalar
from filterpy.common import reshape_z
from constants import TIME_SEND_READ_MESSAGE, TIME_PICTURE, STD_MEASURMENT_ERROR_POSITION
import warnings

DEFAULT_TIME_INCREMENT = TIME_PICTURE + TIME_SEND_READ_MESSAGE


def parse_errors_info_string(string):
    """
    :description:
        Parses a string as encoded by the errors_info_toString function
    :param string: a string encoded by the errors_info_toString function
    :return: [state_error_info, variance_error_info]
    """
    [state_error_info_str, var_error_info_str] = string.split(" ")
    [_, state_error_info_value] = state_error_info_str.split(":")[1]
    [_, var_error_info_value] = var_error_info_str.split(":")[1]
    return state_error_info_value, var_error_info_value


class DistributedKalmanFilter(KalmanFilter):
    """
    Extends the KalmanFilter class from the filterPy library. It implements a distributed Kalman Filter.
    It also adapts the class from filterPy such that it uses the information form of the variance.
    The class is used to implement the DKF such as described in this paper:
          Rao, B. S. Y., Durrant-Whyte, H. F., & Sheen, J. A. (1993).
          A Fully Decentralized Multi-Sensor System For Tracking and Surveillance.
          The International Journal of Robotics Research, 12(1), 20–44. https://doi.org/10.1177/027836499301200102
    """

    def __init__(self, dim_x, dim_z, dt=DEFAULT_TIME_INCREMENT, dim_u=0, model_F=None):

        super().__init__(dim_x, dim_z, dim_u)

        # values used for information form of Kalman equations
        self.PI = eye(dim_x)  # inverse of P (used for information form of KF)
        self.PI_prior = eye(dim_x)  # copy of PI after predict() is called
        self.PI_post = eye(dim_x)  # copy of PI afer update() is called
        self.W = zeros((dim_x, dim_z))  # Kalman gain
        self.x_global = zeros((dim_x, 1))  # global estimate of target state
        self.P_global = eye(dim_x)  # global estimate of covariance matrix
        self.PI_global = eye(dim_x)  # inverse of global estimate P
        self.ti = -1  # timestamp of current measurement
        self.dt = dt  # time difference between measurements
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

    def predict(self, u=None, B=None, F=None, Q=None):
        super().predict(u, B, self.model_F(self.dt), Q)
        self.PI = self.inv(self.P)
        self.PI_prior = self.PI.copy()

    def update(self, z, R=None, H=None, timestamp=-1):

        if timestamp == -1:
            warnings.warn("timestamp not specified: default time increment will be used")

            # timestep set to last time difference between subsequent measurements
            self.dt = DEFAULT_TIME_INCREMENT
            self.ti += DEFAULT_TIME_INCREMENT

        else:
            # timestep set to last time difference between subsequent measurements
            self.dt = timestamp - self.ti
            self.ti = timestamp

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

    # TODO: adapter à x = Fx + Bu
    def assimilate(self, dkf_info_string, ti):
        """
        Assimilates the local estimation recieved from another node to the local estimation of the global state.

        :param (dkf_info_string) dkf_info_string     -- string containing the state/variance error info needed for the
                                                        assimilation step
        :param (int) ti                              -- time of arrival of the other arguments to this
                                                        node. In practice, we have to put the time
        """
        # TODO: comment on sait quant est-ce qu'on a reçu toutes les données ?
        #   --> En fait on sait pas: on fait l'hypothèse que les données s'envoient instantanément et on update à
        #       chaque nouvelle donée reçue.
        #       Par contre, if faut vérifier si la donnée est plus ou moins correcte en regardant si elle est à
        #       une distance plus grande que 2*STD_ERROR de l'estimation locale.

        [state_error_info, variance_error_info] = parse_errors_info_string(dkf_info_string)

        # assumption: no delay between observation being taken at node j and the data arriving at node i (here)
        #   ==> ti ≃ tj    meaning we consider the time
        tj = ti
        delta_t = tj - (self.ti - self.dt)  # δt = tj - τi ≃ ti - τi

        ## Pj_prior: PI(tj|τi) = F(δt)*P(τi|τi)FT(δt) + Q
        Pj_prior = dot(dot(self.model_F(delta_t), self.P_prior), self.model_F(delta_t).T) + self.Q
        PIj_prior = self.inv(Pj_prior)

        ## xj_prior: x(tj|τi) = F(δt)x(τi|τi)
        xj_prior = dot(self.model_F(delta_t), self.x_prior)
        # TODO: +dot(B, u)  --> mais faut voir s'il faut adapter les equa d'assimilation

        # data validation TODO: use a better method
        for diff_pos_in_axis in np.fabs(xj_prior - self.x):
            if diff_pos_in_axis > 2 * STD_MEASURMENT_ERROR_POSITION:
                # invalid data
                return

        # PI(tj|tj) = PI(tj|τi) + variance_error_info
        self.PI_global = PIj_prior + variance_error_info
        self.P_global = self.inv(self.PI_global)

        # x(tj|tj) = P(tj|tj)[PI(tj|τi)x(tj|τi) + state_error_info]
        self.x_global = dot(self.P_global, dot(PIj_prior, xj_prior) + state_error_info)

        # udpate the state and covariance
        self.x = self.x_global.copy()
        self.PI = self.PI_global.copy()
        self.P = self.P_global.copy()

    def state_error_info(self):
        RI = self.inv(self.R)
        return dot(dot(self.H.T, RI), self.z_current)

    def variance_error_info(self):
        RI = self.inv(self.R)
        return dot(dot(self.H.T, RI), self.H)

    def errors_info_toString(self):
        """
        :description:
            Puts the state_error_info and variance_error_info in a nice string.
        :return: state_error_info / variance_error_info & target_id in a string
        """
        s1 = "StateErrorInfo:" + str(self.state_error_info())
        s2 = "VarianceErrorInfo:" + str(self.variance_error_info())
        return s1 + " " + s2

    def get_DKF_info_string(self):
        return self.errors_info_toString()
