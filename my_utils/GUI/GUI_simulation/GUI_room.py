import pygame
import math
import random
from my_utils.GUI.GUI import *
from multi_agent.elements.target import TargetType
from multi_agent.agent.agent import AgentType

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

CAMERA = (200, 0, 0)
PREDICTION = (100, 100, 100)

SET_FIX_COLOR = (0, 100, 200)
MOVING_COLOR = (0, 250, 0)
FIX_COLOR = (250, 0, 0)
UNKNOWN_COLOR = (250,150,0)


class GUI_room:
    def __init__(self, screen, agent, target, x_off, y_off, scale_x, scale_y):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)

        self.agent_to_display = agent
        self.target_to_display = target

        self.x_offset = x_off
        self.y_offset = y_off
        self.scale_x = scale_x
        self.scale_y = scale_y

    def drawRoom(self, tab):

        pygame.draw.rect(self.screen, BLACK, (
            self.x_offset + tab[0] - 10, self.y_offset + tab[1] - 10, self.scale_x * tab[2] + 20,
            self.scale_y * tab[3] + 20))

        pygame.draw.rect(self.screen, WHITE, (
            self.x_offset + tab[0] - 6, self.y_offset + tab[1] - 6, self.scale_x * tab[2] + 12,
            self.scale_y * tab[3] + 12))

        pygame.draw.rect(self.screen, BLACK, (
            self.x_offset + tab[0], self.y_offset + tab[1], self.scale_x * tab[2],
            self.scale_y * tab[3]))

    def draw_one_target(self,target,tab):
        color = WHITE
        if target.type == TargetType.SET_FIX:
            color = SET_FIX_COLOR
        elif target.type == TargetType.FIX:
            color = FIX_COLOR
        elif target.type == TargetType.MOVING:
            color = MOVING_COLOR
        elif target.type == TargetType.UNKNOWN:
            color = UNKNOWN_COLOR

        # so that it is only target.yc drawn in the square
        if (tab[0] <= target.xc + target.radius <= tab[0] + tab[
            2] and tab[1] <= target.yc + target.radius <= tab[1] + tab[3]):  # target inside room
            # render the target.xct
            label = self.font.render(str(target.id), 10, color)
            self.screen.blit(label, (self.x_offset + int(target.xc * self.scale_x) + self.scale_x*target.radius / 2 + 5,
                                     self.y_offset + int(target.yc * self.scale_y) + self.scale_y*target.radius / 2 + 5))
            # render form
            pygame.draw.ellipse(self.screen, color, (
                self.x_offset + int(target.xc * self.scale_x) - self.scale_x * target.radius,
                self.y_offset + int(target.yc * self.scale_y) - self.scale_y * target.radius,
                self.scale_x * target.radius * 2,
                self.scale_y * target.radius * 2))

            if target.radius >= 0.05:
                pygame.draw.ellipse(self.screen, target.color,
                                    (self.x_offset + int(target.xc * self.scale_x) - self.scale_x * target.radius / 2,
                                     self.y_offset + int(target.yc * self.scale_y) - self.scale_y * target.radius / 2,
                                     self.scale_x * target.radius,
                                     self.scale_y * target.radius))

    def drawTarget(self, targets, tab):
        for target in targets:
            self.draw_one_target(target,tab)

    def drawTarget_room_description(self,room,agents_to_display,agentType,allAgents=False):
        agents = []
        if allAgents:
            if agentType == AgentType.AGENT_CAM:
                agents = room.active_AgentCams_list
            elif agentType == AgentType.AGENT_USER:
                agents = room.active_AgentUser_list
        else:
            agents = room.get_multiple_Agent_with_id(agents_to_display, agentType)

        for agent in agents:
             self.drawTarget(agent.room_representation.active_Target_list,room.coordinate_room)


    def drawTarget_all_postion(self, room):
        for target in room.active_Target_list:
            for id in self.target_to_display:
                if target.id == int(id):
                    for position in target.all_position:
                        pygame.draw.circle(self.screen, target.color, (self.x_offset + int(position[0] * self.scale_x),
                                                                       self.y_offset + int(position[1] * self.scale_y)),
                                           1)

    def draw_one_Cam(self, camera, l=100):
            # render text
            label = self.font.render(str(camera.id), 10, CAMERA)
            self.screen.blit(label, (
                self.x_offset + int(camera.xc * self.scale_x) + 5, self.y_offset + int(camera.yc * self.scale_y) + 5))
            # render form
            pygame.draw.circle(self.screen, camera.color, (
                self.x_offset + int(camera.xc * self.scale_x), self.y_offset + int(camera.yc * self.scale_y)), 5)

            color = RED
            if camera.isActive == 1:
                color = GREEN

            pygame.draw.line(self.screen, WHITE, (
                    self.x_offset + int(camera.xc * self.scale_x), self.y_offset + int(camera.yc * self.scale_y)),
                                 (self.x_offset + int(camera.xc * self.scale_x) + l * math.cos(camera.alpha),
                                  self.y_offset + int(camera.yc * self.scale_y) + l * math.sin(camera.alpha)), 2)
            pygame.draw.line(self.screen, color, (
                    self.x_offset + int(camera.xc * self.scale_x), self.y_offset + int(camera.yc * self.scale_y)),
                                 (self.x_offset + int(camera.xc * self.scale_x) + l * math.cos(
                                     camera.alpha - (camera.beta / 2)),
                                  self.y_offset + int(camera.yc * self.scale_y) + l * math.sin(
                                      camera.alpha - (camera.beta / 2))), 2)
            pygame.draw.line(self.screen, color, (
                    self.x_offset + int(camera.xc * self.scale_x), self.y_offset + int(camera.yc * self.scale_y)),
                                 (self.x_offset + int(camera.xc * self.scale_x) + l * math.cos(
                                     camera.alpha + (camera.beta / 2)),
                                  self.y_offset + int(camera.yc * self.scale_y) + l * math.sin(
                                      camera.alpha + (camera.beta / 2))), 2)

    def drawCam(self, room, l=100):
        for agent in room.agentCams_list:
            self.draw_one_Cam(agent.camera,l)

    def drawCam_room_description(self, room, agents_to_display,agentType, allAgents=False):
        """ Draws the previous positions of the selected targets for the selected agents. """
        agents = []
        if allAgents:
            if agentType == AgentType.AGENT_CAM:
                agents = room.active_AgentCams_list
            elif agentType == AgentType.AGENT_USER:
                agents = room.active_AgentUser_list
        else:
            agents = room.get_multiple_Agent_with_id(agents_to_display, agentType)

        for agent in agents:
            self.drawCam(room)

    def drawTraj(self,traj):
        count = 0
        for point in traj:
            count = count + 1
            (x,y) = point
            pygame.draw.circle(self.screen, [255,0,0], (
                self.x_offset + int(x * self.scale_x), self.y_offset + int(y * self.scale_y)), 5)

            label = self.font.render(str(count), 10, CAMERA)
            self.screen.blit(label, (
                self.x_offset + int(x * self.scale_x) + 5, self.y_offset + int(y * self.scale_y) + 5))

    def draw_link_cam_region(self,room,link_cam_to_target):
        for targetAgentLink in link_cam_to_target:
            for agent in room.active_AgentCams_list:
                if agent.id == targetAgentLink.agent_id:
                    for target in room.active_Target_list:
                        if target.id == targetAgentLink.target_id:
                            pygame.draw.line(self.screen, agent.color, (self.x_offset + int(agent.camera.xc * self.scale_x),self.y_offset + int(agent.camera.yc * self.scale_y)),
                                             (self.x_offset + int(target.xc * self.scale_x),self.y_offset + int(target.yc * self.scale_y)),1)

    def draw_link_cam_region_room_description(self,room,agents_to_display,agentType,allAgents=False):
        agents = []
        if allAgents:
            if agentType == AgentType.AGENT_CAM:
                agents = room.active_AgentCams_list
            elif agentType == AgentType.AGENT_USER:
                agents = room.active_AgentUser_list
        else:
            agents = room.get_multiple_Agent_with_id(agents_to_display, agentType)

        for agent_to_display in agents:
            self.draw_link_cam_region(agent_to_display.room_representation,agent_to_display.link_target_agent.link_camera_target)

