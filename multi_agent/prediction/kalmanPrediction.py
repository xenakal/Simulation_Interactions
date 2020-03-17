from constants import NUMBER_PREDICTIONS, TIME_PICTURE, STD_MEASURMENT_ERROR
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag
import numpy as np


class KalmanPrediction:
    """
    Wrapper class using FilterPy to compute the Kalman predictions from the noisy positions
    recorded by the agents.
    The class can be used to Smoothen the results or to make Predictions on future positions.
    """

    def __init__(self):
        # Kalman Filter object
        self.filter = kfObject()
        self.filter.predict()

    def add_measurement(self, z):
        self.filter.update(z)
        self.filter.predict()

    def get_predictions(self):
        for _ in NUMBER_PREDICTIONS:
            pass


def kfObject():
    """ Returns a KalmanFilter object with the model corresponding to our problem. """

    f = KalmanFilter(dim_x=4,
                     dim_z=2)  # as we have a 4d state space and measurements on only the positions (x,y)
    # initial guess on state variables (velocity initiated to 0 arbitrarily => high )
    x_init = 0
    y_init = 0
    vx_init = 0
    vy_init = 0
    f.x = np.array([x_init, y_init, vx_init, vy_init])
    f.F = np.array([[1., 0., TIME_PICTURE, 0.],
                    [0., 1., 0., TIME_PICTURE],
                    [0., 0., 1., 0.],
                    [0., 0., 0., 1.]])
    f.u = 0
    f.H = np.array([[1., 0., 0., 0.],
                    [0., 1., 0., 0.]])
    f.P *= 4.
    f.R = np.eye(10) * STD_MEASURMENT_ERROR ** 2
    f.B = 0
    q = Q_discrete_white_noise(dim=2, dt=TIME_PICTURE, var=0.01)  # var => how precise the model is
    f.Q = block_diag(q, q)
    return f

