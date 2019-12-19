import pygame
from pygame.locals import *
from utils.GUI.GUI import *
from utils.GUI.Button import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

CAMERA = (200, 0, 0)
PREDICTION = (100, 100, 100)

FIX = (200, 120, 0)
TARGET = (0, 250, 0)
OBSTRUCTION = (0, 50, 0)

class GUI_option:
    def __init__(self,screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)

        self.position_mouse = []


        self.modify_option = False
        self.draw_real_trajectory = False
        self.draw_prediction = False
        self.draw_memory_agent = False
        self.draw_memory_all_agent = False
        self.modify_agent = False
        self.modify_target = False

        self.agent_to_display = ["0","1","2"]
        self.target_to_display = ["0","1","2"]


    def update_mouse_position(self):
        self.position_mouse.append([pygame.mouse.get_pos()])

    def suppress_mouse_position(self, position):
        self.position_mouse.remove(position)

    def check_button(self,button):
        for position in self.position_mouse:
            (pos_x,pos_y) = position[0]
            if button.check_click(self.screen,pos_x,pos_y):
                self.suppress_mouse_position(position)
                return True
        return False

    def check_list(self,list):
        for button in list:
            if self.check_button(button):
                for button_to_turn_off in list:
                    button_to_turn_off.set_button(False)
                button.set_button(True)

    def option_add_agent(self,agentID):
        try:
            self.agent_to_display.index(agentID)
        except ValueError:
            self.agent_to_display.append(agentID)

    def option_remove_agent(self, agentID):
        try:
            self.agent_to_display.index(agentID)
            self.agent_to_display.remove(agentID)
        except ValueError:
            pass

    def option_add_target(self,targetID):
        try:
            self.target_to_display.index(targetID)
        except ValueError:
            self.target_to_display.append(targetID)

    def option_remove_target(self, targetID):
        try:
            self.target_to_display.index(targetID)
            self.target_to_display.remove(targetID)
        except ValueError:
            pass

    def draw_option(self):
        x_offset = 0
        y_offset = 40
        y_range = 15
        y_pas = 15

        pygame.draw.rect(self.screen, BLACK, (x_offset, y_offset, 350, 300))

        s = "o - Option modifiable: " + str(self.modify_option)
        label = self.font.render(s, 10, WHITE)
        self.screen.blit(label, (x_offset,y_offset))

        s = "r - real trajectory: " + str(self.draw_real_trajectory)
        label = self.font.render(s, 10, WHITE)
        self.screen.blit(label, (x_offset, y_offset + y_range))
        y_range = y_range+y_pas

        s = "e - memory agent information gathered: " + str(self.draw_memory_all_agent)
        label = self.font.render(s, 10, WHITE)
        self.screen.blit(label, (x_offset, y_offset+y_range))
        y_range = y_range+y_pas

        s = "z - memory agent after fusion: " + str(self.draw_memory_agent)
        label = self.font.render(s, 10, WHITE)
        self.screen.blit(label, (x_offset, y_offset+y_range))
        y_range = y_range+y_pas

        s = "c - modify agent: " + str(self.modify_agent)
        label = self.font.render(s, 10, WHITE)
        self.screen.blit(label, (x_offset, y_offset+y_range))
        y_range = y_range+y_pas

        s = "0-9 - list: " + str(self.agent_to_display)
        label = self.font.render(s, 10, WHITE)
        self.screen.blit(label, (x_offset, y_offset +y_range))
        y_range = y_range+y_pas

        s = "t - modify target: " + str(self.modify_target)
        label = self.font.render(s, 10, WHITE)
        self.screen.blit(label, (x_offset, y_offset+y_range))
        y_range = y_range+y_pas

        s = "0-9 - list: " + str(self.target_to_display)
        label = self.font.render(s, 10, WHITE)
        self.screen.blit(label, (x_offset, y_offset + y_range))


    def option_agent(self,event_key):
        #print(pygame.key.name(event_key))
        add = None

        if event_key == K_0:
            add = "0"
        elif event_key == K_1:
            add = "1"
        elif event_key == K_2:
            add = "2"
        elif event_key == K_3:
            add = "3"
        elif event_key == K_4:
            add = "4"
        elif event_key == K_5:
            add = "5"
        elif event_key == K_6:
            add = "6"
        elif event_key == K_7:
            add = "7"
        elif event_key == K_8:
            add = "8"
        elif event_key == K_9:
            add = "9"

        if add != None:
            try:
                self.agent_to_display.index(add)
                self.agent_to_display.remove(add)
            except ValueError:
                self.agent_to_display.append(add)

    def option_target(self,event_key):
        #print(pygame.key.name(event_key))
        add = None

        if event_key == K_0:
            add = "0"
        elif event_key == K_1:
            add = "1"
        elif event_key == K_2:
            add = "2"
        elif event_key == K_3:
            add = "3"
        elif event_key == K_4:
            add = "4"
        elif event_key == K_5:
            add = "5"
        elif event_key == K_6:
            add = "6"
        elif event_key == K_7:
            add = "7"
        elif event_key == K_8:
            add = "8"
        elif event_key == K_9:
            add = "9"

        if add != None:
            try:
                self.target_to_display.index(add)
                self.target_to_display.remove(add)
            except ValueError:
                self.target_to_display.append(add)


    def option(self,event_key):
        if event_key == K_q:
            self.draw_prediction = not self.draw_prediction
        elif event_key == K_w:
            self.draw_memory_agent = not self.draw_memory_agent
        elif event_key == K_e:
            self.draw_memory_all_agent = not self.draw_memory_all_agent
        elif event_key == K_c:
            self.modify_agent = not self.modify_agent
        elif event_key == K_t:
            self.modify_target = not self.modify_target
        elif event_key == K_r:
            self.draw_real_trajectory = not self.draw_real_trajectory

    def getGUI_Info(self):
        for event in pygame.event.get():
            type_event = event.type
            if type_event == KEYDOWN:
                if event.type == KEYDOWN:
                    if event.key == K_o:
                        self.modify_option = not self.modify_option
                    elif event.key == K_SPACE:
                        pass
                        # print("Take the control of one of the target !")
                    elif event.key == K_ESCAPE:
                        pygame.quit()
                        return False

                    if self.modify_option:
                        self.option(event.key)
                        if self.modify_agent:
                            self.option_agent(event.key)
                        if self.modify_target:
                            self.option_target(event.key)


            elif type_event == MOUSEMOTION and event.buttons[0] == 1: #déplacement + boutton enfoncer
                pass
                #print("Déplacement") #pour utiliser des boutton

            elif type_event == MOUSEBUTTONDOWN: #MOUSEBUTTONUP
                self.update_mouse_position()

        return True