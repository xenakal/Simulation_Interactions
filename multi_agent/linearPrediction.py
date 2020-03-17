import math
import constants
from multi_agent.prediction import Prediction
import numpy as np


def distanceBtwTwoPoint(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))


def avgDirectionFunc(positions):
    """ Returns the direction as the angle (in °) between the horizontal and the line making the direction. """
    if len(positions) <= 1:  # one position or less not enough to calculate direction
        return 0
    prevPos = positions[0]
    avgDir = 0
    counter = 0
    for curPos in positions[1:]:
        dy = curPos[1] - prevPos[1]
        dx = curPos[0] - prevPos[0]
        stepDirection = math.atan2(float(dy), float(dx))
        avgDir += stepDirection

        prevPos = curPos
        counter += 1

    avgDir = avgDir / counter
    #  print("avgDir " + str(avgDir))
    return avgDir


def extractPositionsFromTargetEstimators(prevTargetEstimatorsList):
    """
    :param prevTargetEstimatorsList: a list of target estimators
    :return: a list (max len = PREVIOUS_POSITIONS_USED) containing the extracted positions from each
             TargetEstimator in the list
    """
    if len(prevTargetEstimatorsList) <= 3:
        return []
    if len(prevTargetEstimatorsList) <= constants.PREVIOUS_POSITIONS_USED:
        return [te.position for te in prevTargetEstimatorsList]
    else:
        return [te.position for te in prevTargetEstimatorsList[-constants.PREVIOUS_POSITIONS_USED:]]


class LinearPrediction(Prediction):
    """ Simple & naive linear prediction. """

    def __init__(self, memory, TIME_PICTURE=constants.TIME_PICTURE):
        self.memory = memory
        self.TIMESTEP = TIME_PICTURE

    def makePredictions(self, targetIdList):
        """
        :param targetIdList: list of target IDs for which to estimate the next positions
        :return: a list of lists [[NUMBER_OF_PREDICTIONS*[x_estimated, y_estimated]],...]. len = len(targetIdList)
        """
        predictionsList = []
        for targetID in targetIdList:
            predictedPositions = self.predictTarget(targetID)
            predictionsList.append(predictedPositions)

        return predictionsList

    def predictTarget(self, targetID):
        """
        :param targetID: id of target for which to estimate future positions
        :return: list containing the NUMBER_OF_PREDICTIONS next estimated positions
        """
        #  get previous positions of target
        prevTargetEstimators = self.getPreviousTargetEstimators(targetID)
        prevPositions = extractPositionsFromTargetEstimators(prevTargetEstimators)
        #  estimate the next NUMBER_OF_PREDICTIONS positions
        predictedPositions = self.nextPositions(prevPositions)
        return predictedPositions

    def getPreviousTargetEstimators(self, targetID):
        """
        :return: Returns a list of TargetEstimators corresponding to the previous known positions of the target.
        """
        return self.memory.getPreviousPositions(targetID)

    def calcNextPos(self, position, speed, direction):
        travelDistance = self.TIMESTEP * 4 * speed
        xPrediction = position[0] + math.cos(direction) * travelDistance
        yPrediction = position[1] + math.sin(direction) * travelDistance  # -: the coords are opposite to the cartesian
        return [int(xPrediction), int(yPrediction)]

    def nextPositions(self, prevPosList):
        """ Actual computation of predicted positions. Returns a list (size = NUMBER_PREDICTIONS) of the next estimated
        positions. """

        if len(prevPosList) < 1:
            return []
        currPos = prevPosList[-1]
        prevPos = prevPosList[:-1]
        predictedPos = []

        for i in range(constants.NUMBER_PREDICTIONS):
            #  Estimate next position
            avgSpeed = self.avgSpeedFunc(prevPos)  # calculate average velocity
            avgDirection = avgDirectionFunc(prevPos)  # calculate average direction
            nextPos = self.calcNextPos(currPos, avgSpeed, avgDirection)  # estimate next position
            predictedPos.append(nextPos)
            #  Update needed values
            prevPos = prevPos[1:]  # remove oldest element
            np.append(prevPos, currPos)
            currPos = nextPos

        return predictedPos

    def avgSpeedFunc(self, positions):
        if len(positions) <= 1:  # one position or less not enough to calculate speed
            return 0
        prevPos = positions[0]

        avgSpeed = 0.0
        for curPos in positions:
            stepDistance = distanceBtwTwoPoint(prevPos[0], prevPos[1], curPos[0], curPos[1])
            avgSpeed += stepDistance / self.TIMESTEP
            prevPos = curPos

        avgSpeed = avgSpeed / (len(positions) - 1)
        return avgSpeed

