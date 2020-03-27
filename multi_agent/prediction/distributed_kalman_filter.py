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
        self.x_global = zeros((dim_x, 1))   # global estimate of target state
        self.P_global = eye(dim_x)          # global estimate of covariance matrix
        self.PI_global = eye(dim_x)         # inverse of global estimate P

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

    def assimilate(self, state_error_info, variance_error_info):
        """
        Assimilates the local estimation recieved from another node to the local estimation of the global state.

        :param ([state_error_info, timestamp])      -- state_error_info: list of state error info
                                                       with the corresponding timestamp
        :param ([variance_error_info, timestamp])   -- variance_error_info:list of variance error info
                                                       with the corresponding timestamp
        """
        # TODO: comment on sait quant est-ce qu'on a reçu toutes les données ?
        #   --> En fait on sait pas: on fait l'hypothèse que les données s'envoient instantanément et que les
        #       agents sont synchonisés. A vois si c'est vraiment le cas.
        #       Par contre, on peut vérifier si la donnée est plus ou moins correcte en regardant si elle est à
        #       une distance plus grande que 2*STD_ERROR de l'estimation locale.

        Pjj = 0
        PIji = 0
        xji = 0

        # x(tj|tj) = P(tj|tj)[PI(tj|τi)x(tj|τi) + state_error_info]
        self.x_global = dot(Pjj, dot(PIji, xji) + state_error_info)

        pIji = 0

        # PI(tj|tj) = PI(tj|τi) + variance_error_info
        self.PI_global = PIji + variance_error_info

