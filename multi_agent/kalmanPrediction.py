from multi_agent.linearPrediction import *
from filterpy.kalman import KalmanFilter
import numpy as np


def nextPositionsKF(prevPosList, prevSpeedList):
    """ TODO: MAYBE THIS CAN BE DONE IN THE KF DIRECTLY """
    """ Computation of predicted positions. Returns a list of the next estimated positions. """
    if len(prevPosList) < 1:
        return []
    return [0]


class KalmanPrediction(LinearPrediction):

    def __init__(self, memory):
        super().__init__(memory)

    def getPreviousTargetEstimators(self, targetID):
        """ Same as super method, but filters the previous positions using a Kalman Filter. """
        prevTargetEstimators = super().getPreviousTargetEstimators(targetID)
        filteredPrevTargetEstimators = self.kFilter(prevTargetEstimators)
        return filteredPrevTargetEstimators

    def predictTarget(self, targetID):
        # get previous positions of target
        prevTargetEstimators = super().getPreviousTargetEstimators(targetID)
        prevPositions = extractPositionsFromTargetEstimators(prevTargetEstimators)
        # filter out the positions using a Kalman Filter
        filteredPrevPositions = self.kFilter(prevPositions)
        # estimate the next NUMBER_OF_PREDICTIONS positions
        predictedPositions = nextPositions(filteredPrevPositions)
        return predictedPositions

    def kFilter(self, prevPositions):
        """
        doc: https://filterpy.readthedocs.io/en/latest/kalman/KalmanFilter.html
        :param prevPositions: list containing the previous positions of some target
        :return: the list passed in argument but with a KF applied to filter out noise.
        """
        if len(prevPositions) < 1:
            return []
        f = KalmanFilter(dim_x=4, dim_z=2)  # as we have a 4d state space and measurements on only the positions (x,y)
        # initial guess on state variables (velocity initiated to 0 arbitrarily)
        f.x = np.array([prevPositions[-1][0], prevPositions[-1][1], 0, 0])
        f.F = np.array([[1., 0., TIMESTEP, 0.],
                        [0., 1., 0., TIMESTEP],
                        [0., 0., 1., 0.],
                        [0., 0., 0., 1.]])
        f.H = np.array([[1., 1., 0., 0.]])  # TODO: what is that?
        f.P *= 1.  # defaut value here (eye) TODO: see what is the actual covariance here
        f.R = np.array([[],
                        []])
        return prevPositions
