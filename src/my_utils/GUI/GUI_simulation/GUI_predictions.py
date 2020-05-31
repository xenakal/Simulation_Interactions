import pygame
from src.multi_agent.agent.agent_representation import AgentType
from src import constants

class GUI_predictions:
    """
    Class used to draw the predictions made by each agent.

    :arg method --  which prediction method to use. Choices are :
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
        for agent in myRoom.get_multiple_Agent_with_id(self.agentsToDisplay, AgentType.AGENT_CAM):  # for each agent
            # predictions = agent.makePredictionsOld(self.method, self.targetsToDisplay)
            predictions = agent.get_predictions(self.targetsToDisplay)
            for prediction in predictions:
                for (point, variance) in prediction[1]:
                    pygame.draw.circle(self.screen, agent.color,
                                       (self.xOffset + int(point[0] * self.scaleX),
                                        self.yOffset + int((constants.ROOM_DIMENSION_Y-point[1]) * self.scaleY)), 2)
