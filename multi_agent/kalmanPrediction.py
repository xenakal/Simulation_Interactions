from multi_agent.linearPrediction import *


class KalmanPrediciton(LinearPrediction):

    def __init__(self, memory):
        super().__init__(memory)

    def getPreviousTargetEstimators(self, targetID):
        """ Same as super method, but filters the previous positions using a Kalman Filter. """
        prevTargetEstimators = super().getPreviousTargetEstimators(targetID)
        filteredPrevTargetEstimators = self.kalmanFilter(prevTargetEstimators)
        return filteredPrevTargetEstimators

    def predictTarget(self, targetID):
        # get previous positions of target
        prevTargetEstimators = super().getPreviousTargetEstimators(targetID)
        prevPositions = extractPositionsFromTargetEstimators(prevTargetEstimators)
        # filter out the positions using a Kalman Filter
        filteredPrevPositions = self.kalmanFilter(prevPositions)
        # estimate the next NUMBER_OF_PREDICTIONS positions
        predictedPositions = nextPositions(filteredPrevPositions)
        return predictedPositions

    def kalmanFilter(self, prevPositions):
        """
        :paramprevPositions: list containing the TargetEstimators corresponding to the previous
                                         known positions of some target
        :return: the list passed in argument but with a KF applied to filter out noise.
        """
        # TODO: actually implement the method
        return prevPositions
