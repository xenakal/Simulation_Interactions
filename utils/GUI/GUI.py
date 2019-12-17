import pygame
import copy
from pygame.locals import *
from utils.line import *
from utils.GUI.Button import *
from utils.GUI.option import*
from utils.GUI.GUI_room import*
from utils.GUI.GUI_memories import*
from utils.GUI.GUI_Agent_Target_Detected import *
from utils.GUI.Gui_projection import*

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

BACKGROUND = RED

class GUI:
    def __init__(self):
        pygame.init()
        # pygame.display.init()
        # self.screen = pygame.display.set_mode((1220, 960), pygame.RESIZABLE)
        self.w = 800
        self.h = 600
        self.screen = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE)

        self.button_menu = ButtonList(["Simulation","Camera","Stat","Option"],10,-30,0,0,100,30)
        self.button_simulation_1 = ButtonList(["real T", "M agent","M all agent"], 10, -20, 0, 40, 100, 20)
        self.button_simulation_2 = ButtonList(["0", "1", "2","3","4","5","6"], -35, 10, 700, 40, 35, 15)
        self.button_simulation_3 = ButtonList(["0", "1", "2","3","4","5","6"], -35, 10, 750, 40, 35, 15)

        self.GUI_option = GUI_option(self.screen)

        self.GUI_room = GUI_room(self.screen,self.GUI_option.agent_to_display,self.GUI_option.target_to_display,200,100,400,400)
        self.GUI_memories = GUI_memories(self.screen,self.GUI_option.agent_to_display,self.GUI_option.target_to_display,200,100,4/3,4/3)

        self.GUI_projection = GUI_projection(self.screen)
        self.GUI_ATD = GUI_Agent_Target_Detected(self.screen)

        pygame.display.set_caption("Camera simulation")
        self.font = pygame.font.SysFont("monospace", 15)

    def refresh(self):
        pygame.draw.rect(self.screen, BLACK, (0,0,self.w,self.h))

    def display_menu(self):
        self.GUI_option.check_list(self.button_menu.list)
        self.button_menu.draw(self.screen)

    def display_simulation_button(self):
        for button in self.button_simulation_1.list:
            self.GUI_option.check_button(button)

        for button in self.button_simulation_2.list:
            self.GUI_option.check_button(button)
            if button.pressed:
                self.GUI_option.option_add_agent(button.text)
            else:
                self.GUI_option.option_remove_agent(button.text)

        for button in self.button_simulation_3.list:
            self.GUI_option.check_button(button)
            if button.pressed:
                self.GUI_option.option_add_target(button.text)
            else:
                self.GUI_option.option_remove_target(button.text)

        self.button_simulation_1.draw(self.screen)
        self.button_simulation_2.draw(self.screen)
        self.button_simulation_3.draw(self.screen)


    def updateScreen(self):
        pygame.display.update()




