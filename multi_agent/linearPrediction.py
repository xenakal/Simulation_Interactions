import math

from multi_agent.prediction import Prediction, NUMBER_PREDICTIONS, TIMESTEP


def nextPositions(prevTargetEstimators):
    """ Actual computation of predicted positions. Returns a list (size = NUMBER_PREDICTIONS) of the next estimated
    positions. """

    if len(prevTargetEstimators) <= 3:
        return []
    prevPos = [te.position for te in prevTargetEstimators[:-1]]
    currPos = prevTargetEstimators[-1].position
    predictedPos = []

    for i in range(NUMBER_PREDICTIONS):
        #  Estimate next position
        avgSpeed = avgSpeedFunc(prevPos)  # calculate average velocity
        avgDirection = avgDirectionFunc(prevPos)  # calculate average direction
        nextPos = calcNextPos(currPos, avgSpeed, avgDirection)  # estimate next position
        predictedPos.append(nextPos)
        #  Update needed values
        prevPos = prevPos[1:]  # remove oldest element
        prevPos.append(currPos)  # include new pos for next iteration
        currPos = nextPos

    return predictedPos


def avgSpeedFunc(positions):
    if len(positions) <= 1:  # one position or less not enough to calculate speed
        return 0
    prevPos = positions[0]
    stepTime = 1  # TODO: see what the actual time increment is
    avgSpeed = 0.0
    for curPos in positions:
        stepDistance = distanceBtwTwoPoint(prevPos[0], prevPos[1], curPos[0], curPos[1])
        avgSpeed += stepDistance / stepTime
        prevPos = curPos

    avgSpeed = avgSpeed / (len(positions) - 1)
    return avgSpeed


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


def calcNextPos(position, speed, direction):
    travelDistance = TIMESTEP * 4 * speed
    xPrediction = position[0] + math.cos(direction) * travelDistance
    yPrediction = position[1] + math.sin(direction) * travelDistance  # -: the coordinates are opposite to the cartesian
    return [int(xPrediction), int(yPrediction)]


class LinearPrediction(Prediction):
    """ Simple & naive linear prediction. """

    def __init__(self, memory):
        self.memory = memory

    def makePredictions(self, targetIdList):
        """
        :param targetIdList: list of target IDs for which to estimate the next positions
        :return: a list [[NUMBER_OF_PREDICTIONS*[x_estimated, y_estimated]],...]. len = len(targetIdList)
        """
        predictionsList = []
        for targetID in targetIdList:
            prediction = []
            #  get previous positions of target
            prevTargetEstimators = self.memory.getPreviousPositions(targetID)
            predictedPos = nextPositions(prevTargetEstimators)
            prediction += predictedPos
            predictionsList.append(prediction)

        return predictionsList
