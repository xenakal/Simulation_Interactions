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

        self.agent_to_display = []
        self.target_to_display = []


    def update_mouse_position(self):
        self.position_mouse.append([pygame.mouse.get_pos()])

    def suppress_mouse_position(self, position):
        self.position_mouse.remove(position)

    def reset_mouse_list(self):
        self.position_mouse = []

    def check_button(self,button):
        for position in self.position_mouse:
            (pos_x,pos_y) = position[0]
            if button.check_click(self.screen, pos_x, pos_y):
                self.suppress_mouse_position(position)
                return True
        return False

    def check_list(self, buttons):
        for button in buttons:
            if self.check_button(button):
                for button_to_turn_off in buttons:
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

    def getGUI_Info(self):
        for event in pygame.event.get():
            type_event = event.type
            if type_event == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    return (False, False)
                if event.key == K_r:
                    return (True, True)

            elif type_event == MOUSEMOTION and event.buttons[0] == 1: #déplacement + boutton enfoncer
                pass
                #print("Déplacement") #pour utiliser des boutton

            elif type_event == MOUSEBUTTONDOWN: #MOUSEBUTTONUP
                self.update_mouse_position()

        return (True, False)