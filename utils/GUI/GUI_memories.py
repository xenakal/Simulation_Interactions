import pygame
from utils.GUI.GUI import*

class GUI_memories:
    def __init__(self, screen,agent,target,x_off,y_off,scaleX,scaleY):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)

        self.agent_to_display = agent
        self.target_to_display = target

        self.x_offset = x_off
        self.y_offset = y_off
        self.scale_x = scaleX
        self.scale_y = scaleY


    def drawMemory(self, myRoom):
        for agent in myRoom.agentCam:
            for id_agent_to_draw in self.agent_to_display:
                if agent.id == int(id_agent_to_draw):
                    for target in myRoom.targets:
                        for estimator in agent.memory.memory_agent.get_target_list(target.id):
                            for id_target_to_draw in self.target_to_display:
                                if estimator.target_ID == int(id_target_to_draw):
                                    pygame.draw.circle(self.screen, agent.color,
                                                       (self.x_offset+int(estimator.position[0]*self.scale_x), self.y_offset+int(estimator.position[1]*self.scale_y)), 2)


    def drawMemoryAll(self, myRoom):
        for agent_to_draw in myRoom.agentCam:
            for id_agent_to_draw in self.agent_to_display:
                if agent_to_draw.id == int(id_agent_to_draw):
                    for agent in myRoom.agentCam:
                        for target in myRoom.targets:
                            for estimator in agent.memory.memory_all_agent.get_estimator_time_target_agent(-1, target.id,
                                                                                                           agent.id):
                                for id_target_to_draw in self.target_to_display:
                                    if estimator.target_ID == int(id_target_to_draw):
                                        pygame.draw.circle(self.screen, agent.color,
                                                           (self.x_offset+int(estimator.position[0]*self.scale_x),self.y_offset+int(estimator.position[1]*self.scale_y)), 2)