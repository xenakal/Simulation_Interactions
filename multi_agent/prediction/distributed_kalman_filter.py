from filterpy.kalman import KalmanFilter
import numpy as np
from numpy import eye, dot, zeros, isscalar
from filterpy.common import reshape_z


class DistributedKalmanFilter(KalmanFilter):
    """
    Extends the KalmanFilter class from the filterPy library. It implements a distributed Kalman Filter.
    It also adapts the class from filterPy such that it uses the information form of the variance.
    The class is used to implement the DKF as described in this paper:
          Rao, B. S. Y., Durrant-Whyte, H. F., & Sheen, J. A. (1993).
          A Fully Decentralized Multi-Sensor System For Tracking and Surveillance.
          The International Journal of Robotics Research, 12(1), 20–44. https://doi.org/10.1177/027836499301200102
    """

    def __init__(self, dim_x, dim_z, dim_u=0):
        super().__init__(dim_x, dim_z, dim_u)

        # values used for information form of Kalman equations
        self.PI = eye(dim_x)                # inverse of P (used for information form of KF)
        self.PI_prior = eye(dim_x)          # copy of PI after predict() is called
        self.PI_post = eye(dim_x)           # copy of PI afer update() is called
        self.W = zeros((dim_x, dim_z))      # Kalman gain
        self.global_x = zeros((dim_x, 1))   # global estimate of target state
        self.global_P = eye(dim_x)          # global estimate of covariance matrix
        self.global_PI = eye(dim_x)         # inverse of global estimate P

    def predict(self, u=None, B=None, F=None, Q=None):
        super().predict(u, B, F, Q)
        self.PI = self.inv(self.P)
        self.PI_prior = self.PI.copy()

    def update(self, z, R=None, H=None):
        # set to None to force recompute
        self._log_likelihood = None
        self._likelihood = None
        self._mahalanobis = None

        if z is None:
            self.z = np.array([[None]*self.dim_z]).T
            self.x_post = self.x.copy()
            self.P_post = self.P.copy()
            self.y = zeros((self.dim_z, 1))
            return

        z = reshape_z(z, self.dim_z, self.x.ndim)

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

    def assimilate(self, state_error_info_list, variance_error_info_list):
        """
        Assimilates the local estimations in the global estimation equations
        :param ([state_error_info, timestamp]) state_error_info_list: list of state
        :param variance_error_info_list:
        """