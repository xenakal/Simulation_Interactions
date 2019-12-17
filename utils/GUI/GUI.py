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

BACKGROUND = RED

class GUI:
    def __init__(self):
        pygame.init()
        # pygame.display.init()
        # self.screen = pygame.display.set_mode((1220, 960), pygame.RESIZABLE)
        self.w = 800
        self.h = 500
        self.screen = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE)

        self.buttonList = ButtonList(["Simulation","Camera","Stat","Option"],10,-30,0,0,100,30)

        self.GUI_option = GUI_option(self.screen)

        self.GUI_room = GUI_room(self.screen,self.GUI_option.agent_to_display,self.GUI_option.target_to_display,50,50,400,400)
        self.GUI_memories = GUI_memories(self.screen,self.GUI_option.agent_to_display,self.GUI_option.target_to_display,50,50,4/3,4/3)

        self.GUI_projection = GUI_projection(self.screen)
        self.GUI_ATD = GUI_Agent_Target_Detected(self.screen)

        pygame.display.set_caption("Camera simulation")
        self.font = pygame.font.SysFont("monospace", 15)

    def refresh(self):
        pygame.draw.rect(self.screen, BLACK, (0,0,self.w,self.h))

    def display_menu(self):
        self.GUI_option.check_list(self.buttonList.list)
        self.buttonList.draw(self.screen)

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


