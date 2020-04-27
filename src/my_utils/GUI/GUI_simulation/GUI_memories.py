import pygame
from src.multi_agent.agent.agent import AgentType
from src import constants

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

    def drawMemory(self, room, allAgents=False):
        """ Draws the previous positions of the selected targets for the selected agents. """

        if allAgents:
            agents = room.active_AgentCams_list
        else:
            agents = room.get_multiple_Agent_with_id(self.agents_to_display, AgentType.AGENT_CAM)

        for agent in agents:
            for targetID in self.targets_to_display:
                agentMemory = agent.memory
                # draw previous target positions as read by the agent
                for targetEstimator in agentMemory.get_previous_positions(targetID):
                    pygame.draw.circle(self.screen, agent.camera.color,
                                       (self.x_offset + int(targetEstimator.item_position[0] * self.scale_x),
                                        self.y_offset + int((constants.ROOM_DIMENSION_Y-targetEstimator.item_position[1])* self.scale_y)), 2)

                # draw positions with noise "removed" as estimated by the Kalman Filter
                for targetEstimator in agentMemory.get_noiseless_estimations(targetID):
                    pygame.draw.circle(self.screen, (255, 51, 255),
                                       (self.x_offset + int(targetEstimator.item_position[0] * self.scale_x),
                                        self.y_offset + int((constants.ROOM_DIMENSION_Y-targetEstimator.item_position[1])* self.scale_y)), 2)
               
                # draw internal memory of positions used for the Kalman Filtering
                """
                predictor = agentMemory.get_target_predictor(targetID)
                if predictor is not None:
                    for pos in predictor.kalman_memory:
                        pygame.draw.circle(self.screen, (204, 0, 0),
                                           (self.x_offset + int(pos[0] * self.scale_x),
                                            self.y_offset + int(pos[1] * self.sscale_y)), 2)                        
                """

    def draw_mesure_and_receiveMessages(self, room):
        """ Draws the previous positions of the selected targets for the selected agents. """
        agents = room.get_multiple_Agent_with_id(self.agents_to_display, AgentType.AGENT_CAM)

        for agent in agents:
            for targetID in self.targets_to_display:
                agentMemory = agent.memory
                for allAgent in room.active_AgentCams_list:
                    for targetEstimator in agentMemory.getPreviousPositions_allMessages(targetID, allAgent.id):
                        pygame.draw.circle(self.screen, agent.camera.color,
                                           (self.x_offset + int(targetEstimator.item_position[0] * self.scale_x),
                                            self.y_offset + int((constants.ROOM_DIMENSION_Y-targetEstimator.item_position[1]) * self.scale_y)), 2)
