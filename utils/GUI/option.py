import pygame
from pygame.locals import *

class GUI_option:
    def __init__(self):
        self.modify_option = False
        self.draw_prediction = False
        self.draw_memory_agent = False
        self.draw_memory_all_agent = False
        self.modify_agent = False
        self.modify_target = False

        self.agent_to_display = []
        self.target_to_display = []

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
                        return False

                    if self.modify_option:
                        self.option(event.key)
                        if self.modify_agent:
                            self.option_agent(event.key)
                        if self.modify_target:
                            self.option_target(event.key)


            elif type_event == MOUSEMOTION and event.buttons[0] == 1:
                pass
                # print("Button pressed") #pour utiliser des boutton

        return True