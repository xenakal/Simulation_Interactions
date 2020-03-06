from multi_agent.linearPrediction import *
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag
import numpy as np
from multi_agent.estimator import STD_MEASURMENT_ERROR


# TODO: maybe refactor to have only one Kalman Filter object per agent instead of creating a new one every time
class KalmanPrediction(LinearPrediction):

    def __init__(self, memory, TIME_PICTURE):
        super().__init__(memory, TIME_PICTURE)

    def predictTarget(self, targetID):
        # return self.predictTargetSmoothing(targetID)
        return self.predictTargetPrediction(targetID)

    def predictTargetPrediction(self, targetID):
        # get previous positions of target
        prevTargetEstimators = super().getPreviousTargetEstimators(targetID)
        prevPositions = extractPositionsFromTargetEstimators(prevTargetEstimators)
        # filter out the positions using a Kalman Filter
        predictedPositions = self.kPredictor(prevPositions)
        return predictedPositions

    def predictTargetSmoothing(self, targetID):
        # get previous positions of target
        prevTargetEstimators = super().getPreviousTargetEstimators(targetID)
        prevPositions = extractPositionsFromTargetEstimators(prevTargetEstimators)
        # filter out the positions using a Kalman Filter
        smoothenedPrevPositions = self.kSmoother(prevPositions)
        # estimate the next NUMBER_OF_PREDICTIONS positions
        predictedPositions = self.nextPositions(smoothenedPrevPositions)
        return predictedPositions

    def kfObject(self, prevPositions):
        """ Returns a KalmanFilter object with the model corresponding to our problem. """

        f = KalmanFilter(dim_x=4, dim_z=2)  # as we have a 4d state space and measurements on only the positions (x,y)
        # initial guess on state variables (velocity initiated to 0 arbitrarily => high )
        x_init = prevPositions[-1][0]
        y_init = prevPositions[-1][1]
        vx_init = 0
        vy_init = 0
        f.x = np.array([x_init, y_init, vx_init, vy_init])
        f.F = np.array([[1., 0., self.TIMESTEP, 0.],
                        [0., 1., 0., self.TIMESTEP],
                        [0., 0., 1., 0.],
                        [0., 0., 0., 1.]])
        f.u = 0
        f.H = np.array([[1., 0., 0., 0.],
                        [0., 1., 0., 0.]])
        f.P *= 4.
        f.R = np.eye(2) * STD_MEASURMENT_ERROR ** 2
        f.B = 0
        q = Q_discrete_white_noise(dim=2, dt=self.TIMESTEP, var=0.01)  # var => how precise the model is
        f.Q = block_diag(q, q)
        return f

    def kSmoother(self, prevPositions):
        """
        Doc: https://filterpy.readthedocs.io/en/latest/kalman/KalmanFilter.html
        Book by the creator of FilerPy, explaining the exact problem we have here:
            https://drive.google.com/file/d/0By_SW19c1BfhSVFzNHc0SjduNzg/view (see chapter 8).
        :param prevPositions: list containing the previous positions of some target
        :return: the list passed in argument but with a KF applied to filter out noise.
        """

        if len(prevPositions) < 1:
            return []

        tracker = self.kfObject(prevPositions)
        # process data with kalman filter
        mu, cov, _, _ = tracker.batch_filter(prevPositions)
        # smoothen result
        (xs, Ps, Ks, Pp) = tracker.rts_smoother(mu, cov)

        return xs

    def kPredictor(self, prevPositions):
        """
        :param prevPositions:
        :return:
        """

        if len(prevPositions) < 1:
            return []

        tracker = self.kfObject(prevPositions)
        # process data with kalman filter
        mu, cov, _, _ = tracker.batch_filter(prevPositions)
        # smoothen result
        (xs, Ps, Ks, Pp) = tracker.rts_smoother(mu, cov)

        # predict next positions
        predictions = []
        tracker.predict()
        prediction, P = tracker.get_prediction()
        state = [prediction[0], prediction[1]]
        predictions.append(state)
        for _ in range(NUMBER_PREDICTIONS):
            tracker.update(np.array(state))
            tracker.predict()
            prediction, _ = tracker.get_prediction()
            state = [prediction[0], prediction[1]]
            predictions.append(state)

        return predictions
