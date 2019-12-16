import pygame
import copy
from pygame.locals import *
from utils.line import *
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

CAMERA = (200, 0, 0)
PREDICTION = (100, 100, 100)

FIX = (200, 120, 0)
TARGET = (0, 250, 0)
OBSTRUCTION = (0, 50, 0)

class GUI:
    def __init__(self):
        pygame.init()
        # pygame.display.init()
        # self.screen = pygame.display.set_mode((1220, 960), pygame.RESIZABLE)
        self.screen = pygame.display.set_mode((800, 500), pygame.RESIZABLE)

        self.GUI_option = GUI_option()

        self.GUI_room = GUI_room(self.screen)
        self.GUI_memories = GUI_memories(self.screen,self.GUI_option.agent_to_display,self.GUI_option.target_to_display)
        self.GUI_projection = GUI_projection(self.screen)
        self.GUI_ATD = GUI_Agent_Target_Detected(self.screen)

        pygame.display.set_caption("Camera simulation")
        self.font = pygame.font.SysFont("monospace", 15)


    def updateScreen(self):
        pygame.display.update()





    #  Used if cameras are used (if agents, then use drawPredictions)
    def drawPredictionsOld(self, myRoom):
        for camera in myRoom.cameras:
            for target in myRoom.targets:
                camTargetsDetected = [x[0] for x in camera.targetDetectedList]
                if (target in camera.predictedPositions and target in camTargetsDetected):
                    self.drawTargetPrediction(target, camera.predictedPositions[target])

    def drawPredictions(self, myRoom):
        for agent in myRoom.agentCam:
            for target in myRoom.targets:
                pass
                #if (target in agent.memory.predictedPositions):
                    #self.drawTargetPrediction(target, agent.memory.predictedPositions[target])

    # predictionPos is a list with the N next predicted positions
    def drawTargetPrediction(self, target, predictionPos):
        predictedTarget = copy.deepcopy(target)
        predictionPos.insert(0, [predictedTarget.xc, predictedTarget.yc])
        pygame.draw.lines(self.screen, PREDICTION, False, predictionPos)


class Button:
    def __init__(self,x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.label = "test"
        self.color_released = WHITE
        self.color_pressed = YELLOW
        self.color_mouse_on = BLUE
        self.color_label = BLACK

        self.pressed = False

    def draw(self,window):
        if self.check_mouse_pos(window):
            pygame.draw.rect(window, self.color_mouse_on, Rect(self.x, self.y, self.w, self.h))
        else:
            if self.pressed:
                pygame.draw.rect(window,self.color_pressed,Rect(self.x,self.y,self.w,self.h))
            else:
                pygame.draw.rect(window, self.color_released, Rect(self.x, self.y, self.w, self.h))

    def check_mouse_pos(self,window):
        (pos_x,pos_y) = pygame.mouse.get_pos()
        if (pos_x > self.x and pos_x < self.x+self.w) and (pos_y > self.y and pos_y < self.y+self.h):
            return True
        else:
            return  False

    def check_mouse_clik(self,window):
        self.draw(window)
        if self.check_mouse_pos(window):
            if pygame.mouse.get_pressed:
                self.pressed = not self.pressed