from multi_agent.linearPrediction import *
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag
import numpy as np
from multi_agent.estimator import STD_MEASURMENT_ERROR


def kfObject(prevPositions):
    """ Returns a KalmanFilter object with the model corresponding to our problem. """

    f = KalmanFilter(dim_x=4, dim_z=2)  # as we have a 4d state space and measurements on only the positions (x,y)
    # initial guess on state variables (velocity initiated to 0 arbitrarily => high )
    f.x = np.array([prevPositions[-1][0], prevPositions[-1][1], 0, 0])
    f.F = np.array([[1., 0., TIMESTEP, 0.],
                    [0., 1., 0., TIMESTEP],
                    [0., 0., 1., 0.],
                    [0., 0., 0., 1.]])
    f.u = 0
    f.H = np.array([[1., 0., 0., 0.],
                    [0., 1., 0., 0.]])
    f.P *= 100.  # defaut value here (eye) TODO: see what is the actual covariance here.
    f.R = np.eye(2) * STD_MEASURMENT_ERROR**2
    f.B = 0
    q = Q_discrete_white_noise(dim=2, dt=TIMESTEP, var=0.01)  # var => how approximate the model is
    f.Q = block_diag(q, q)
    return f


def kSmoother(prevPositions):
    """
    Doc: https://filterpy.readthedocs.io/en/latest/kalman/KalmanFilter.html
    Book by the creator of FilerPy, explaining the exact problem we have here:
        https://drive.google.com/file/d/0By_SW19c1BfhSVFzNHc0SjduNzg/view (see chapter 8).
    :param prevPositions: list containing the previous positions of some target
    :return: the list passed in argument but with a KF applied to filter out noise.
    """

    if len(prevPositions) < 1:
        return []

    tracker = kfObject(prevPositions)
    mu, cov, _, _ = tracker.batch_filter(prevPositions)
    # smoothen result
    (xs, Ps, Ks, Pp) = tracker.rts_smoother(mu, cov)

    return xs


def kPredictor(prevPositions):
    """

    :param prevPositions:
    :return:
    """
    if len(prevPositions) < 1:
        return []

    tracker = kfObject(prevPositions)
    mu, cov, _, _ = tracker.batch_filter(prevPositions)
    # smoothen result
    (xs, Ps, Ks, Pp) = tracker.rts_smoother(mu, cov)

    predictions = []
    for _ in range(NUMBER_PREDICTIONS):
        prediction = tracker.get_prediction()
        predictions.append(prediction)

    return predictions


class KalmanPrediction(LinearPrediction):

    def __init__(self, memory):
        super().__init__(memory)

    def predictTarget(self, targetID):
        return self.predictTargetSmoothing(targetID)

    def predictTargetKPrediction(self, targetID):
        # get previous positions of target
        prevTargetEstimators = super().getPreviousTargetEstimators(targetID)
        prevPositions = extractPositionsFromTargetEstimators(prevTargetEstimators)
        # filter out the positions using a Kalman Filter
        predictedPositions = kPredictor(prevPositions)
        return predictedPositions

    def predictTargetSmoothing(self, targetID):
        # get previous positions of target
        prevTargetEstimators = super().getPreviousTargetEstimators(targetID)
        prevPositions = extractPositionsFromTargetEstimators(prevTargetEstimators)
        # filter out the positions using a Kalman Filter
        smoothenedPrevPositions = kSmoother(prevPositions)
        # estimate the next NUMBER_OF_PREDICTIONS positions
        predictedPositions = nextPositions(smoothenedPrevPositions)
        return predictedPositions

