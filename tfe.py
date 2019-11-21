# -*- coding: utf-8 -*-
import numpy
import math
import pygame
from pygame.locals import*

#WHITE = pygame.Color(255, 255, 255)
 
class Camera:
    def __init__(self,cam_id,cam_x,cam_y,cam_alpha,cam_beta):
        #Label
        self.cam_id     = cam_id
        self.cam_status = 'agent'
        
        #Location on the map
        self.xc = cam_x
        self.yc = cam_y
        self.alpha = math.radians(cam_alpha) #deg rotation 
        self.beta = math.radians(cam_beta) #deg view angle
        
        #Detection
        self.targetList = []
        
    def takePicture(self,TargetList):
        #In first approach to avoid to remove items, list is emptied at the start
        self.targetList = []
        
        #Check to see if the target is in the field
        x1 = self.xc + math.cos(self.alpha-self.beta/2)
        y1 = self.yc + math.sin(self.alpha-self.beta/2)
        x2 = self.xc + math.cos(self.alpha+self.beta/2)
        y2 = self.yc + math.sin(self.alpha+self.beta/2)
        
        m1 = (self.yc-y1)/(self.xc-x1)
        m2 = (self.yc-y2)/(self.xc-x2)
        
        for target in targetList:
             margin1 = m1*(target.xc - self.xc) + self.yc
             margin2 = m2*(target.xc - self.xc) + self.yc
             
        #A vérifier si le calcul des droite est ok   
             #if(lowerMarign >= 0 & upperMargin <= 0):
                # self.targetDetectList.append(target)
        
      
    
    def analysePicture():
        print('analysing picture')
    
    def sendMessageToCam():
        print('sending message')
    
    def writeOnTheWhiteBoard():
        print('writting on the white board')
        
class Target:
     def __init__(self,tar_id,tar_x,tar_y,tar_color):
        #Label
        self.tar_shape = "round"
        self.tar_id    = tar_id
        self.tar_color = tar_color
        
        #Location on the map
        self.xc = tar_x
        self.yc = tar_y
        
        #size
        self.size = 10
        
class Room:
    def __init__(self):
        self.shape = "square"                       
        self.coord = numpy.array([10,10,300,300])    #x y l h
        self.targets = []
        self.cameras = []
        self.camerasNumber = 0
        self.targetNumber = 0 
      
    def createTargets(self,tar_x,tar_y,tar_color):
        for n in tar_x:
            self.targets.append(Target(self.targetNumber,tar_x[self.targetNumber],tar_y[self.targetNumber],
                                   tar_color[self.targetNumber]))
            self.targetNumber  = self.targetNumber+1
        
    def removeTarget(self):
        print('removed')
    
    def createCameras(self,cam_x,cam_y,cam_alpha,cam_beta):
        for n in cam_x:
            self.cameras.append(Camera(self.camerasNumber,cam_x[self.camerasNumber],
                                       cam_y[self.camerasNumber],cam_alpha[self.camerasNumber]
                                       ,cam_beta[self.camerasNumber]))
            self.camerasNumber = self.camerasNumber+1
    
    def removeCamera(self,cam_x,cam_y,cam_alpha,cam_beta):
        print('removed')
        

class GUI:
    def __init__(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((640, 480))
    
    def drawRoom(self,tab,color = 0):
        pygame.draw.rect(self.screen, (255, 255, 255),(tab[0],tab [1],tab[2],tab[3]))
        
    def drawTarget(self,x,y,size,color = 0 ):
        pygame.draw.circle(self.screen,(0,255,0),(x,y),size)
    
    def drawCam(self,x,y,alpha,beta,color = 0 , l = 50):
        pygame.draw.circle(self.screen,(255,0,0),(x,y),5)
        pygame.draw.line(self.screen,(255,0,0),(x,y),(x+l*math.cos(alpha-beta/2),y+l*math.sin(alpha-beta/2)), 2) 
        pygame.draw.line(self.screen,(255,0,0),(x,y),(x+l*math.cos(alpha+beta/2),y+l*math.sin(alpha+beta/2)), 2)
        
    def updateScreen(self):
        pygame.display.update() 
        

def init():
    #Options for the targets
    x_tar = numpy.array([55,270])
    y_tar = numpy.array([55,140])
    color_tar = numpy.array(['red','red'])
    #Options for the cameras
    x_cam = numpy.array([10,310,10,310,])
    y_cam = numpy.array([10,10,310,310])
    angle_cam = numpy.array([45,135,315,225])
    angle_view_cam = numpy.array([60,60,60,60])
    #Creating the room, the target and the camera
    myRoom = Room()
    myRoom.createTargets(x_tar,y_tar,color_tar)
    myRoom.createCameras(x_cam,y_cam,angle_cam,angle_view_cam)
    
    #setting the GUI interface
    myGUI = GUI()
    myGUI.drawRoom(myRoom.coord)
    
    for target in myRoom.targets:
        myGUI.drawTarget(target.xc,target.yc,target.size) 
                                       
    for camera in myRoom.cameras:    
        myGUI.drawCam(camera.xc,camera.yc,camera.alpha,camera.beta)
    
    myGUI.updateScreen()
    
    
       
def main(): 
    init()
    
    while(True): #Boucle d'événements
        for event in pygame.event.get(): #parcours de la liste des événements
            if(event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE)): #interrompt la boucle si nécessaire
                break
    pygame.quit()
    
    

if __name__ == "__main__":
    # execute only if run as a script
    main()