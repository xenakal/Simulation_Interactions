import pygame
import math
from src import constants
from src.multi_agent.agent.agent_interacting_room_camera import AgentCam
from src.multi_agent.agent.agent_representation import AgentType
from src.multi_agent.elements.mobile_camera import MobileCameraType
from src.multi_agent.elements.target import TargetType

import src.multi_agent.elements.camera as cam

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 125, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128,128,128)

CAMERA = (200, 0, 0)
PREDICTION = (100, 100, 100)
CAMERA_FIX = (255, 0, 0)
CAMERA_ROTATIVE = (0, 0, 125)
CAMERA_RAIL = (0, 255, 0)
CAMERA_FREE = (255, 255, 0)

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
    def __init__(self, screen, agent, target, x_off, y_off, scale_x, scale_y,GUI_option):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)
        self.GUI_option = GUI_option

        self.agent_to_display = agent
        self.target_to_display = target

        self.x_offset = x_off
        self.y_offset = y_off
        self.scale_x = scale_x
        self.scale_y = scale_y


    def draw_vector(self,color,x,y,length,alpha):
        x=x-3
        y=y+3

        pt1 = (x,y)
        pt2 =(x+length*math.cos(alpha),y+length*math.sin(alpha))
        angle = math.pi/16
        l = 0.8*length
        pt3 = (x+math.cos(alpha+angle)*l,y+math.sin(alpha+angle)*l)
        pt4 = (x+math.cos(alpha-angle)*l,y+math.sin(alpha-angle)*l)

        pygame.draw.line(self.screen, color, pt1, pt2, 5)
        pygame.draw.line(self.screen, color, pt2, pt3, 5)
        pygame.draw.line(self.screen, color, pt2, pt4, 5)

    def draw_grid(self):
        for x in range(constants.ROOM_DIMENSION_X):
            pt1 = (self.x_offset+self.scale_x*x,self.y_offset)
            pt2 = (self.x_offset+self.scale_x*x,self.y_offset+self.scale_y*constants.ROOM_DIMENSION_Y)
            pygame.draw.line(self.screen, GRAY, pt1, pt2, 1)

        for y in range(constants.ROOM_DIMENSION_Y):
            pt1 = (self.x_offset,self.y_offset+self.scale_y*y)
            pt2 = (self.x_offset+self.scale_x*constants.ROOM_DIMENSION_X,self.y_offset+self.scale_y*y)
            pygame.draw.line(self.screen, GRAY, pt1, pt2, 1)

    def draw_axis(self):
        color = RED
        pt_center = (self.x_offset,self.y_offset+self.scale_y*constants.ROOM_DIMENSION_Y)
        self.draw_vector(color,pt_center[0],pt_center[1],self.scale_x,0)
        self.draw_vector(color,pt_center[0], pt_center[1], self.scale_y,math.radians(-90))

        label = self.font.render("x", 20, color)
        self.screen.blit(label, (self.x_offset+self.scale_x,self.y_offset+self.scale_y*constants.ROOM_DIMENSION_Y))
        label = self.font.render("y", 20, color)
        self.screen.blit(label, (self.x_offset-25,self.y_offset+self.scale_y*(constants.ROOM_DIMENSION_Y-1)))


    def draw_all_target_room_description(self, room, agents_to_display, agentType, allAgents=False):
        for agent in get_agent_to_draw(room, agents_to_display, agentType, allAgents):
            self.draw_all_target(agent.room_representation.target_representation_list, room.coordinate_room)

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

        if self.GUI_option.show_grid:
            self.draw_grid()
        self.draw_axis()

    def draw_all_target(self, targets, tab):
        for target in targets:
            self.draw_one_target(target, tab)

    def draw_one_target(self, target, tab):
        color = WHITE
        if target.target_type == TargetType.SET_FIX:
            color = SET_FIX_COLOR
        elif target.target_type  == TargetType.FIX:
            color = FIX_COLOR
        elif target.target_type  == TargetType.MOVING:
            color = MOVING_COLOR
        elif target.target_type  == TargetType.UNKNOWN:
            color = UNKNOWN_COLOR

        if target.confidence == [-1,-1]:
            color_conf = WHITE
        elif target.confidence[1] <= constants.CONFIDENCE_THRESHOLD:
            color_conf = RED
        elif target.confidence[1] >= 0:
            new_delta = target.confidence[1] - constants.CONFIDENCE_THRESHOLD
            new_scale = (255 / (constants.CONFIDENCE_MAX_VALUE - constants.CONFIDENCE_THRESHOLD))
            value =new_scale*new_delta
            R  = max(min(255-value,255),0)
            G = max(min(value, 255), 0)
            color_conf = (int(R),int(G), 0)


        pt_center = (self.x_offset + int(target.xc * self.scale_x),self.y_offset + int((constants.ROOM_DIMENSION_Y-target.yc) * self.scale_y))
        # so that it is only target.yc drawn in the squarer

        # render the target.xct
        label = self.font.render(str(target.id), 10, color)
        self.screen.blit(label,(pt_center[0] + int(self.scale_x * target.radius / 2*1.5),
                              pt_center[1]+ int(self.scale_y * target.radius/2*1.5)))
        # render form

        pygame.draw.ellipse(self.screen, color_conf, (
                pt_center[0] - int(self.scale_x * (target.radius * 1.2)),
                pt_center[1] - int(self.scale_y * (target.radius * 1.2)),
                int(self.scale_x * (target.radius * 1.2) * 2),
                int(self.scale_y * (target.radius * 1.2) * 2)))

        pygame.draw.ellipse(self.screen, color, (
                pt_center[0] - int(self.scale_x * target.radius),
                pt_center[1] - int(self.scale_y * target.radius),
                int(self.scale_x * target.radius * 2),
                int(self.scale_y * target.radius * 2)))

        if target.radius >= 0.05:
               pygame.draw.ellipse(self.screen, target.color,
                                    (pt_center[0] - int(self.scale_x * target.radius / 2),
                                     pt_center[1]- int(self.scale_y * target.radius / 2),
                                     int(self.scale_x * target.radius),
                                     int(self.scale_y * target.radius)))

        if not target.variance_on_estimation is None:
            facteur = 1
            value_to_draw1 = 0
            value_to_draw2 = 0

            if not isinstance(target.variance_on_estimation,(int,int)):
                value_to_draw1 = target.variance_on_estimation[0] #+ target.radius
                value_to_draw2 = target.variance_on_estimation[1] #+ target.radius

                pt_1 =   (pt_center[0]+ int(facteur * value_to_draw1 * math.cos(target.alpha) * self.scale_x),
                pt_center[1]+ int(facteur * value_to_draw1 * math.sin(target.alpha) * self.scale_y))

                pt_2 = (pt_center[0]+ int(facteur * value_to_draw1 * math.cos(target.alpha+ math.pi)* self.scale_x) ,
                pt_center[1]+ int(facteur * value_to_draw1 * math.sin(target.alpha+ math.pi)* self.scale_y) )

                pt_3 = (pt_center[0]+ int(facteur * value_to_draw1 * math.cos(target.alpha+ math.pi/2)* self.scale_x) ,
                pt_center[1]+ int(facteur * value_to_draw2 * math.sin(target.alpha+ math.pi/2)* self.scale_y))

                pt_4 = (pt_center[0]+ int(facteur * value_to_draw1 * math.cos(target.alpha- math.pi/2)* self.scale_x) ,
                pt_center[1]+ int(facteur * value_to_draw2 * math.sin(target.alpha- math.pi/2)* self.scale_y))


                pygame.draw.line(self.screen, WHITE, pt_center,pt_1, 3)
                pygame.draw.line(self.screen, WHITE, pt_center, pt_2, 3)
                pygame.draw.line(self.screen, WHITE, pt_center, pt_3, 3)
                pygame.draw.line(self.screen, WHITE, pt_center, pt_4, 3)

        pygame.draw.circle(self.screen, RED, (pt_center[0] + int(target.radius*self.scale_x*math.cos(target.alpha)),
                                              pt_center[1] + int(target.radius*self.scale_y*math.sin(target.alpha))), 3)

    def draw_one_target_all_previous_position(self, room):
        for target in room.information_simulation.target_list:
            for id in self.target_to_display:
                if target.id == int(id):
                    for position in target.all_position:
                        pygame.draw.circle(self.screen, target.color, (self.x_offset + int(position[0] * self.scale_x),
                                                                       self.y_offset + int((constants.ROOM_DIMENSION_Y-position[1]) * self.scale_y)),1)

    def draw_all_agentCam(self, cam_list):
        for agent in cam_list:
            camera = cam.get_camera_agentCam_vs_agentCamRepresentation(agent)
            pt_center = (self.x_offset + int(camera.xc * self.scale_x),
                         self.y_offset + int((constants.ROOM_DIMENSION_Y - camera.yc) * self.scale_y))

            label = self.font.render(str(camera.id), 10, CAMERA)
            self.screen.blit(label, (pt_center[0]+7, pt_center[1] + 7))

            self.draw_one_camera(camera)
            if isinstance(agent,AgentCam) and  self.GUI_option.show_virtual_cam and not agent.virtual_camera is None :
                self.draw_one_camera(agent.virtual_camera,True)

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


            pygame.draw.circle(self.screen, color_conf,pt_center, 11)
            pygame.draw.circle(self.screen, BLACK, pt_center, 9)
            pygame.draw.circle(self.screen, color, pt_center, 8)
            pygame.draw.circle(self.screen, camera.color,pt_center, 5)

            if camera.camera_type == MobileCameraType.RAIL or camera.camera_type == MobileCameraType.FREE and self.GUI_option.show_point_to_reach:
                if isinstance(agent, AgentCam):
                    if len(agent.memory_of_position_to_reach) > 0:
                            mem = agent.memory_of_position_to_reach[-1]
                            if len(mem) > 2:
                                print("problem"+str(mem))
                            (x, y, index) = mem[0]
                            pt = (self.x_offset + int(x * self.scale_x), self.y_offset + int((constants.ROOM_DIMENSION_Y-y) * self.scale_y))
                            pygame.draw.circle(self.screen, RED, pt, 5)

                            if camera.camera_type == MobileCameraType.FREE:
                                (x, y, index) = mem[1]
                                pt = (self.x_offset + int(x * self.scale_x),
                                      self.y_offset + int((constants.ROOM_DIMENSION_Y - y) * self.scale_y))
                                pygame.draw.circle(self.screen, GREEN, pt, 5)

                    if len(agent.memory_of_objectives) > 0:
                            xt = agent.memory_of_objectives[-1][0]
                            yt = agent.memory_of_objectives[-1][1]
                            angle = agent.memory_of_objectives[-1][2]
                            length = 0.5
                            pt1 = (self.x_offset + int(xt * self.scale_x), self.y_offset + int((constants.ROOM_DIMENSION_Y-yt) * self.scale_y))
                            pt2 = (self.x_offset + int((xt + length * math.cos(angle)) * self.scale_x),
                                   self.y_offset + int((constants.ROOM_DIMENSION_Y-(yt + length * math.sin(angle))) * self.scale_y))
                            pygame.draw.line(self.screen, agent.color, pt1, pt2, 3)
                            pygame.draw.circle(self.screen, WHITE, pt1, 3)

    def draw_one_camera(self, camera,virtual = False):
        l = camera.field_depth * math.pow((math.pow(self.scale_x * math.cos(camera.alpha), 2) + math.pow(self.scale_y * math.sin(camera.alpha), 2)), 0.5)
        pt_center = (self.x_offset + int(camera.xc * self.scale_x),self.y_offset + int((constants.ROOM_DIMENSION_Y - camera.yc) * self.scale_y))
        pt_alpha = (pt_center[0] + l * math.cos(camera.alpha),pt_center[1] - l * math.sin(camera.alpha))
        pt_beta_plus = (pt_center[0] +  l * math.cos(camera.alpha + (camera.beta / 2)), pt_center[1] - l * math.sin(camera.alpha + (camera.beta / 2)))
        pt_beta_moins = (pt_center[0] +  l * math.cos(camera.alpha - (camera.beta / 2)), pt_center[1] - l * math.sin(camera.alpha - (camera.beta / 2)))

        if camera.camera_type == MobileCameraType.FIX:
            color_type = CAMERA_FIX
        elif camera.camera_type == MobileCameraType.ROTATIVE:
            color_type = CAMERA_ROTATIVE
        elif camera.camera_type == MobileCameraType.RAIL:
            color_type = CAMERA_RAIL
        elif camera.camera_type == MobileCameraType.FREE:
            color_type = CAMERA_FREE

        color = RED
        if camera.is_active:
            color = GREEN
        if virtual:
            color = (0, 125, 125)

        if not virtual:
            pygame.draw.circle(self.screen, color_type, pt_center,13)

        if self.GUI_option.show_field_cam:
            pygame.draw.line(self.screen, WHITE, pt_center,pt_alpha, 2)
            pygame.draw.line(self.screen, color, pt_center,pt_beta_plus,2)
            pygame.draw.line(self.screen, color, pt_center,pt_beta_moins,2)
            try:
                pygame.draw.arc(self.screen, color, [pt_center[0] - int(l),pt_center[1]- int(l), 2 * l, 2 * l],camera.alpha - (camera.beta / 2), camera.alpha + (camera.beta / 2), 2)
            except ValueError:
                print("Error draw cam")

            self.draw_a_trajectory(camera.trajectory.trajectory, camera.color)

    def draw_a_trajectory(self, traj, color):
        for n in range(len(traj) - 1):
            x1, y1 = traj[n]
            x2, y2 = traj[n + 1]

            pt1 = (self.x_offset + int(x1 * self.scale_x), self.y_offset + int((constants.ROOM_DIMENSION_Y-y1) * self.scale_y))
            pt2 = (self.x_offset + int(x2 * self.scale_x), self.y_offset + int((constants.ROOM_DIMENSION_Y-y2) * self.scale_y))
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
                for elem in targetAgentLink.agentDistance_list:
                    if agent.id == elem.agent_id:
                        for target in room.target_representation_list:
                            if target.id == targetAgentLink.target_id:
                                pygame.draw.line(self.screen, agent.color, (
                                    self.x_offset + int(camera.xc * self.scale_x),
                                    self.y_offset + int((constants.ROOM_DIMENSION_Y-camera.yc)* self.scale_y)),
                                                 (self.x_offset + int(target.xc * self.scale_x),
                                                  self.y_offset + int((constants.ROOM_DIMENSION_Y-target.yc) * self.scale_y)), 1)
