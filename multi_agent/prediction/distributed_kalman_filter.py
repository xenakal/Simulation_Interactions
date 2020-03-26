from filterpy.kalman import KalmanFilter
import numpy as np
from numpy import eye, dot, zeros, isscalar
from filterpy.common import reshape_z


class DistributedKalmanFilter(KalmanFilter):
    """
    Extends the KalmanFilter class from the filterPy library. It implements a distributed Kalman Filter.
    """

    def __init__(self, dim_x, dim_z, dim_u=0):
        super().__init__(dim_x, dim_z, dim_u)

        # values used for information form of Kalman equations
        self.PI = eye(dim_x)       # inverse of P (used for information form of KF)
        self.W = zeros((dim_x, dim_z))

    def predict(self, u=None, B=None, F=None, Q=None):
        super().predict(u, B, F, Q)
        self.PI = self.inv(self.P)

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

        # needed for Kalman gain matrix
        self.P = self.inv(self.PI)

        # Kalman gain matrix
        # W = P*HT*RI
        self.W = dot(dot(self.P, H.T), RI)

        # x = x + Wy
        self.x = self.x + dot(self.W, self.y)

    def assimilate(self, ):
        pass