import pygame
from utils.GUI.GUI import *


class GUI_memories:

    def __init__(self, screen, agents, targets, x_off, y_off, scaleX, scaleY):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)

        self.agents_to_display = agents
        self.targets_to_display = targets

        self.x_offset = x_off
        self.y_offset = y_off
        self.scale_x = scaleX
        self.scale_y = scaleY

    def drawMemory(self, myRoom, allAgents=False):
        """ Draws the previous positions of the selected targets for the selected agents. """
        if allAgents:
            agents = myRoom.agentCams
        else:
            agents = myRoom.getAgentsWithIDs(self.agents_to_display)

        for agent in agents:
            for targetID in self.targets_to_display:
                agentMemory = agent.memory
                for targetEstimator in agentMemory.getPreviousPositions(targetID):
                    pygame.draw.circle(self.screen, agent.color,
                                       (self.x_offset + int(targetEstimator.position[0] * self.scale_x),
                                        self.y_offset + int(targetEstimator.position[1] * self.scale_y)), 2)
