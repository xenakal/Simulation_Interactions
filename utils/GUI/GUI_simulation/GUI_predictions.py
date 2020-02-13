import pygame


class GUI_predictions:
    """
    Class used to draw the predictions made by each agent.

    :arg method --  which prediction method to use. Choices are:
                        =1 : linear prediction
                        =2 : kalman
    """

    def __init__(self, screen, agents, targets, x_off, y_off, scaleX, scaleY, method):
        self.screen = screen
        self.agentsToDisplay = agents
        self.targetsToDisplay = targets
        self.method = method
        self.xOffset = x_off
        self.yOffset = y_off
        self.scaleX = scaleX
        self.scaleY = scaleY

    def drawPredictions(self, myRoom):
        for agent in myRoom.getAgentsWithIDs(self.agentsToDisplay):  # for each agent
            predictions = agent.makePredictions(self.method, self.targetsToDisplay)
            for prediction in predictions:
                for point in prediction:
                    pygame.draw.circle(self.screen, agent.color,
                                       (self.xOffset + int(point[0] * self.scaleX),
                                        self.yOffset + int(point[1] * self.scaleY)), 2)

    """
    def drawPredictions(self, myRoom):
        for agent in myRoom.agentCam:
            for target in myRoom.targets:
                pass
                #if (target in agent.memory.predictedPositions):
                    #self.drawTargetPrediction(target, agent.memory.predictedPositions[target])


    # predictionPos is a list with the N next predicted positions
    def drawTargetPrediction(self, target, predictionPos):
        predictedTarget = copy.deepcopy(target)
        predictionPos.insert(0, [predictedTarget.xc, predictedTarget.yc])
        pygame.draw.lines(self.screen, PREDICTION, False, predictionPos)
    """
