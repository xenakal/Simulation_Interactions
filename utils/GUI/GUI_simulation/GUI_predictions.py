import pygame

class GUI_predictions:

    def __init__(self, screen, agents, targets, x_off, y_off, scaleX, scaleY):
        self.screen = screen
        self.agents = agents
        self.targets = targets

    def drawPredictions(self, myRoom):
        for agent in myRoom.agentCam: # for each agent
            pass

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