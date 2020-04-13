import pygame
import math
from src import constants
from src.multi_agent.agent.agent_interacting_room_camera import AgentCam
from src.multi_agent.elements.mobile_camera import MobileCameraType
from src.multi_agent.elements.room import Room
from src.multi_agent.elements.target import TargetType
from src.multi_agent.agent.agent import AgentType
import src.multi_agent.elements.camera as cam

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 125, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

CAMERA = (200, 0, 0)
PREDICTION = (100, 100, 100)

SET_FIX_COLOR = (0, 100, 200)
MOVING_COLOR = (0, 250, 0)
FIX_COLOR = (250, 0, 0)
UNKNOWN_COLOR = (250, 150, 0)


def get_agent_to_draw(room, agents_to_display, agentType, allAgents=False):
    agents = []
    if allAgents:
        if agentType == AgentType.AGENT_CAM:
            agents = room.information_simulation.agentCams_list
        elif agentType == AgentType.AGENT_USER:
            agents = room.information_simulation.agentUser_list
    else:
        agents = room.get_multiple_Agent_with_id(agents_to_display, agentType)
    return agents


class GUI_room_representation():
    def __init__(self, screen, agent, target, x_off, y_off, scale_x, scale_y):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)

        self.agent_to_display = agent
        self.target_to_display = target

        self.x_offset = x_off
        self.y_offset = y_off
        self.scale_x = scale_x
        self.scale_y = scale_y

    def draw_all_target_room_description(self, room, agents_to_display, agentType, allAgents=False):
        for agent in get_agent_to_draw(room, agents_to_display, agentType, allAgents):
            self.draw_all_target(agent.room_representation.active_Target_list, room.coordinate_room)

    def draw_agentCam_room_description(self, room, agents_to_display, agentType, allAgents=False):
        for agent in get_agent_to_draw(room, agents_to_display, agentType, allAgents):
            self.draw_all_agentCam(agent.room_representation.agentCams_representation_list)

    def draw_link_cam_region_room_description(self, room, agents_to_display, agentType, allAgents=False):
        for agent_to_display in get_agent_to_draw(room, agents_to_display, agentType, allAgents):
            self.draw_link_cam_region(agent_to_display.room_representation,
                                      agent_to_display.link_target_agent.link_camera_target)

    def draw_room(self, tab, draw_time=False):
        if draw_time:
            label = self.font.render("time = %.02f s" % constants.get_time(), 10, WHITE)
            self.screen.blit(label, (self.x_offset, self.y_offset - 30))

        pygame.draw.rect(self.screen, BLACK, (
            self.x_offset + tab[0] - 10, self.y_offset + tab[1] - 10, self.scale_x * tab[2] + 20,
            self.scale_y * tab[3] + 20))

        pygame.draw.rect(self.screen, WHITE, (
            self.x_offset + tab[0] - 6, self.y_offset + tab[1] - 6, self.scale_x * tab[2] + 12,
            self.scale_y * tab[3] + 12))

        pygame.draw.rect(self.screen, BLACK, (
            self.x_offset + tab[0], self.y_offset + tab[1], self.scale_x * tab[2],
            self.scale_y * tab[3]))

    def draw_all_target(self, targets, tab):
        for target in targets:
            self.draw_one_target(target, tab)

    def draw_one_target(self, target, tab):
        color = WHITE
        if target.type == TargetType.SET_FIX:
            color = SET_FIX_COLOR
        elif target.type == TargetType.FIX:
            color = FIX_COLOR
        elif target.type == TargetType.MOVING:
            color = MOVING_COLOR
        elif target.type == TargetType.UNKNOWN:
            color = UNKNOWN_COLOR

        color_conf = WHITE
        if target.confidence_pos > 0:
            color_conf = [math.ceil(255 - 2.5 * target.confidence_pos), math.ceil(target.confidence_pos * 2.5), 0]

        pygame.draw.ellipse(self.screen, color_conf, (
            self.x_offset + int(target.xc * self.scale_x) - int(self.scale_x * (target.radius * 1.2)),
            self.y_offset + int(target.yc * self.scale_y) - int(self.scale_y * (target.radius * 1.2)),
            int(self.scale_x * (target.radius * 1.2) * 2),
            int(self.scale_y * (target.radius * 1.2) * 2)))

        # so that it is only target.yc drawn in the square
        if (tab[0] <= target.xc + target.radius <= tab[0] + tab[
            2] and tab[1] <= target.yc + target.radius <= tab[1] + tab[3]):  # target inside room
            # render the target.xct
            label = self.font.render(str(target.id), 10, color)
            self.screen.blit(label,
                             (self.x_offset + int(target.xc * self.scale_x) + int(self.scale_x * target.radius / 2) + 5,
                              self.y_offset + int(target.yc * self.scale_y) + int(
                                  self.scale_y * target.radius / 2) + 5))
            # render form
            pygame.draw.ellipse(self.screen, color, (
                self.x_offset + int(target.xc * self.scale_x) - int(self.scale_x * target.radius),
                self.y_offset + int(target.yc * self.scale_y) - int(self.scale_y * target.radius),
                int(self.scale_x * target.radius * 2),
                int(self.scale_y * target.radius * 2)))

            if target.radius >= 0.05:
                pygame.draw.ellipse(self.screen, target.color,
                                    (self.x_offset + int(target.xc * self.scale_x) - int(
                                        self.scale_x * target.radius / 2),
                                     self.y_offset + int(target.yc * self.scale_y) - int(
                                         self.scale_y * target.radius / 2),
                                     int(self.scale_x * target.radius),
                                     int(self.scale_y * target.radius)))

        if not target.variance_on_estimation is None:
            # if not target.variance_on_estimation[0] is None and  target.variance_on_estimation[1] is None and not target.variance_on_estimation == (0,0):

            facteur = 1
            value_to_draw1 = target.variance_on_estimation[0] + target.radius
            value_to_draw2 = target.variance_on_estimation[1] + target.radius

            pygame.draw.line(self.screen, WHITE, (
            self.x_offset + int(target.xc * self.scale_x), self.y_offset + int(target.yc * self.scale_y)),
                             (self.x_offset + int(
                                 (target.xc + facteur * value_to_draw1 * math.cos(target.alpha)) * self.scale_x),
                              self.y_offset + int(
                                  (target.yc + facteur * value_to_draw1 * math.sin(target.alpha)) * self.scale_y)), 3)

            pygame.draw.line(self.screen, WHITE, (
                self.x_offset + int(target.xc * self.scale_x), self.y_offset + int(target.yc * self.scale_y)),
                             (self.x_offset + int(
                                 (target.xc + facteur * value_to_draw1 * math.cos(
                                     target.alpha + math.pi)) * self.scale_x),
                              self.y_offset + int(
                                  (target.yc + facteur * value_to_draw1 * math.sin(
                                      target.alpha + math.pi)) * self.scale_y)), 3)

            pygame.draw.line(self.screen, WHITE, (
                self.x_offset + int(target.xc * self.scale_x), self.y_offset + int(target.yc * self.scale_y)),
                             (self.x_offset + int(
                                 (target.xc + facteur * value_to_draw2 * math.cos(
                                     target.alpha + math.pi / 2)) * self.scale_x),
                              self.y_offset + int(
                                  (target.yc + facteur * value_to_draw2 * math.sin(
                                      target.alpha + math.pi / 2)) * self.scale_y)), 3)

            pygame.draw.line(self.screen, WHITE, (
                self.x_offset + int(target.xc * self.scale_x), self.y_offset + int(target.yc * self.scale_y)),
                             (self.x_offset + int(
                                 (target.xc + facteur * value_to_draw2 * math.cos(
                                     target.alpha - math.pi / 2)) * self.scale_x),
                              self.y_offset + int(
                                  (target.yc + facteur * value_to_draw2 * math.sin(
                                      target.alpha - math.pi / 2)) * self.scale_y)), 3)

        pygame.draw.circle(self.screen, RED, (
            self.x_offset + int(target.xc * self.scale_x + target.radius * self.scale_x * math.cos(target.alpha)),
            self.y_offset + int(target.yc * self.scale_y + target.radius * self.scale_y * math.sin(target.alpha))), 3)

    def draw_one_target_all_previous_position(self, room):
        for target in room.information_simulation.target_list:
            for id in self.target_to_display:
                if target.id == int(id):
                    for position in target.all_position:
                        pygame.draw.circle(self.screen, target.color, (self.x_offset + int(position[0] * self.scale_x),
                                                                       self.y_offset + int(position[1] * self.scale_y)),
                                           1)

    def draw_all_agentCam(self, cam_list):
        for agent in cam_list:
            camera = cam.get_camera_agentCam_vs_agentCamRepresentation(agent)
            label = self.font.render(str(camera.id), 10, CAMERA)
            self.screen.blit(label, (
                self.x_offset + int(camera.xc * self.scale_x) + 5, self.y_offset + int(camera.yc * self.scale_y) + 5))

            self.draw_one_camera(camera)
            # render form
            if not agent.is_active:
                color = RED
            else:
                color = GREEN

            if agent.confidence > 5:
                color_conf = GREEN
            elif agent.confidence > 3:
                color_conf = ORANGE
            elif agent.confidence == -1:
                color_conf = WHITE
            else:
                color_conf = RED

            pygame.draw.circle(self.screen, color_conf, (
                self.x_offset + int(camera.xc * self.scale_x), self.y_offset + int(camera.yc * self.scale_y)), 11)

            pygame.draw.circle(self.screen, BLACK, (
                self.x_offset + int(camera.xc * self.scale_x), self.y_offset + int(camera.yc * self.scale_y)), 9)

            pygame.draw.circle(self.screen, color, (
                self.x_offset + int(camera.xc * self.scale_x), self.y_offset + int(camera.yc * self.scale_y)), 8)

            pygame.draw.circle(self.screen, camera.color, (
                self.x_offset + int(camera.xc * self.scale_x), self.y_offset + int(camera.yc * self.scale_y)), 5)

            if camera.camera_type == MobileCameraType.RAIL or camera.camera_type == MobileCameraType.FREE:
                if isinstance(agent, AgentCam):
                    if len(agent.memory_of_position_to_reach) > 0:
                        for mem in agent.memory_of_position_to_reach[-1]:
                            (x, y, index) = mem
                            pygame.draw.circle(self.screen, RED, (
                                self.x_offset + int(x * self.scale_x), self.y_offset + int(y * self.scale_y)), 3)

                    if len(agent.memory_of_objectives) > 0:
                        xt = agent.memory_of_objectives[-1][0]
                        yt = agent.memory_of_objectives[-1][1]
                        angle = agent.memory_of_objectives[-1][2]
                        length = 0.5
                        pt1 = (self.x_offset + int(xt * self.scale_x), self.y_offset + int(yt * self.scale_y))
                        pt2 = (self.x_offset + int((xt + length * math.cos(angle)) * self.scale_x),
                               self.y_offset + int((yt + length * math.sin(angle)) * self.scale_y))
                        pygame.draw.line(self.screen, agent.color, pt1, pt2, 3)
                        pygame.draw.circle(self.screen, WHITE, pt1, 3)

    def draw_one_camera(self, camera):
        l = camera.field_depth * math.pow((math.pow(self.scale_x * math.cos(camera.alpha), 2) + math.pow(
            self.scale_y * math.sin(camera.alpha), 2)), 0.5)

        color = RED
        if camera.is_active == 1:
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
        """
            pt1 =  (self.x_offset + int(camera.xc * self.scale_x) + l * math.cos(
                            camera.alpha - (camera.beta / 2)),
                         self.y_offset + int(camera.yc * self.scale_y) + l * math.sin(
                             camera.alpha - (camera.beta / 2)))

            pt2 =  (self.x_offset + int(camera.xc * self.scale_x) + l * math.cos(
                                 camera.alpha + (camera.beta / 2)),
                              self.y_offset + int(camera.yc * self.scale_y) + l * math.sin(
                                  camera.alpha + (camera.beta / 2)))
            pygame.draw.line(self.screen, color, pt1, pt2, 2)
            """
        try:
            pygame.draw.arc(self.screen, color, [self.x_offset + int(camera.xc * self.scale_x) - int(l),
                                                 self.y_offset + int(camera.yc * self.scale_y) - int(l), 2 * l, 2 * l],
                            -camera.alpha - (camera.beta / 2), -camera.alpha + (camera.beta / 2), 2)
        except ValueError:
            print("Error draw cam")

        self.draw_a_trajectory(camera.trajectory.trajectory, camera.color)

    def draw_a_trajectory(self, traj, color):
        for n in range(len(traj) - 1):
            x1, y1 = traj[n]
            x2, y2 = traj[n + 1]

            pt1 = (self.x_offset + int(x1 * self.scale_x), self.y_offset + int(y1 * self.scale_y))
            pt2 = (self.x_offset + int(x2 * self.scale_x), self.y_offset + int(y2 * self.scale_y))
            pygame.draw.line(self.screen, color, pt1, pt2, 2)
            pygame.draw.circle(self.screen, color, pt1, 5)
            pygame.draw.circle(self.screen, color, pt2, 5)

            label = self.font.render(str(n), 10, CAMERA)
            self.screen.blit(label, (pt1[0] + 5, pt1[1] + 5))
            label = self.font.render(str(n + 1), 10, CAMERA)
            self.screen.blit(label, (pt2[0] + 5, pt2[1] + 5))

    def draw_link_cam_region(self, room, link_cam_to_target):

        for targetAgentLink in link_cam_to_target:
            for agent in room.agentCams_representation_list:
                camera = cam.get_camera_agentCam_vs_agentCamRepresentation(agent)
                if agent.id == targetAgentLink.agent_id:
                    for target in room.active_Target_list:
                        if target.id == targetAgentLink.target_id:
                            pygame.draw.line(self.screen, agent.color, (
                                self.x_offset + int(camera.xc * self.scale_x),
                                self.y_offset + int(camera.yc * self.scale_y)),
                                             (self.x_offset + int(target.xc * self.scale_x),
                                              self.y_offset + int(target.yc * self.scale_y)), 1)
