# -*- coding: utf-8 -*-
import numpy
import math
import time
import pygame
from pygame.locals import*

WHITE  = (255, 255, 255)
BLACK  = (0,0,0)
RED    = (255, 0, 0)
BLUE   = (0, 0, 255)
GREEN  = (0, 255, 0)
CAMERA = (200, 0, 0)

FIX    = (200, 120, 0)
TARGET = (0, 250, 0)
OBSTRUCTION = (0, 50, 0)

 
class Camera:
    def __init__(self,cam_id,cam_x,cam_y,cam_alpha,cam_beta):
        #Label
        self.id     = cam_id
        self.status = 'agent'
        
        #Location on the map
        self.xc = cam_x
        self.yc = cam_y
        self.alpha = math.radians(cam_alpha) #deg rotation 
        self.beta = math.radians(cam_beta) #deg view angle
        
        #Detection
        self.targetDetectedList = []
        
    def takePicture(self,targetList):
        #In first approach to avoid to remove items, list is emptied at the start
        self.targetList = []
        
        #Compute the field seen by the camera
        #alph, beta are fix now but we could imagine to change alpha, so better to compute it every time.
        x1 = self.xc + math.cos(self.alpha-self.beta/2)
        y1 = self.yc + math.sin(self.alpha-self.beta/2)
        x2 = self.xc + math.cos(self.alpha+self.beta/2)
        y2 = self.yc + math.sin(self.alpha+self.beta/2)
        
        m1 = (self.yc-y1)/(self.xc-x1)
        m2 = (self.yc-y2)/(self.xc-x2)
        
        #finding the the perpendicular to those line
        p1 = -(1/m1)
        p2 = -(1/m2)
        
        
        for target in targetList:
             #check done like if object is a point without radius
             margin1 = (m1*(target.xc - self.xc) + self.yc)-target.yc
             margin2 = (m2*(target.xc - self.xc) + self.yc)-target.yc
            
             #finding the perpendicular crossing the target's center
             #computing the x and y  were the two line intersect
             xi1 = (p1*target.xc-m1*self.xc+self.yc-target.yc)/(p1-m1)
             yi1 = m1*(xi1-self.xc)+self.yc    #yi1 = p1*(xi1-target.xc)+target.yc 
             xi2 = (p2*target.xc-m2*self.xc+self.yc-target.yc)/(p2-m2)
             yi2 = m2*(xi2-self.xc)+self.yc    #yi2 = p2*(xi2-target.xc)+target.yc 
             #computing distance between the center and the camera field limite
             d1 = math.pow(math.pow((xi1 - target.xc),2)+math.pow((yi1 - target.yc),2),0.5)
             d2 = math.pow(math.pow((xi2 - target.xc),2)+math.pow((yi2 - target.yc),2),0.5)
        
             if((margin1 >= 0 and margin2 <= 0) or (margin1 <= 0 and margin2 >= 0) or d1 <= target.size or d2 <= target.size):
                self.targetDetectedList.append(target)
                print("cam " + str(self.id) + " detect target target " + str(target.id))
                
        
        #1) il faut également toujours modéliser le fait que si deux bojets sont les un derrière les autres
        #alors la camera ne le vois pas.
        
    def analysePicture():
        print('analysing picture')
    
    def sendMessageToCam():
        print('sending message')
    
    def writeOnTheWhiteBoard():
        print('writting on the white board')
  
  
class Target:
     def __init__(self,tar_id,tar_x,tar_y,tar_vx,tar_vy,tar_label,tar_size):
        #Label
        self.shape = "round"
        self.id    = tar_id
        self.label = tar_label
        
        #Location on the map
        self.xc = tar_x
        self.yc = tar_y
        
        #Speeds
        if(tar_label == 'fix'):
            self.vx = 0
            self.vy = 0
        else:
            self.vx = tar_vx 
            self.vy = tar_vy
        
        #size
        self.size = tar_size
        
     def mooveTarget(self,time):
         #easy solution need to be investeagted
         self.xc = self.xc + self.vx * time
         self.yc = self.yc + self.vy * time   
 
 
class Room:
    def __init__(self):
        #Room attributes                  
        self.coord = numpy.array([10,10,300,300])    #x y l h
        #target in the room
        self.targets = []
        self.targetNumber = 0
        #camera in the room
        self.cameras = []
        self.camerasNumber = 0
        
      
    def createTargets(self,tar_x,tar_y,tar_vx,tar_vy,tar_label,tar_size):
        for n in tar_x:
            self.targets.append(Target(self.targetNumber,tar_x[self.targetNumber],tar_y[self.targetNumber],
                                       tar_vx[self.targetNumber],tar_vy[self.targetNumber],tar_label[self.targetNumber]
                                       ,tar_size[self.targetNumber]))
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
        pygame.init()
        #pygame.display.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.font = pygame.font.SysFont("monospace", 15)

    
    def drawRoom(self,tab,color = 0):
        pygame.draw.rect(self.screen, WHITE,(tab[0],tab [1],tab[2],tab[3]))
        
    def drawTarget(self,x,y,size,tar_id,label,tab):
        color = RED
        if label == "fix":
            color = FIX
        elif label == "target":
            color = TARGET
        elif label == "obstruction":
            color = OBSTRUCTION
            
        #so that it is only draw in the square
        if(x+size >= tab[0] and x+size <= tab[0]+tab[2] and y+size >= tab[1] and y+size <= tab[1]+tab[3]):
            # render text
            label = self.font.render(str(tar_id), 10, color)
            self.screen.blit(label, (x+size/2+5,y+size/2+5))
            # render form
            pygame.draw.circle(self.screen,color,(x,y),size)
        
    def drawCam(self,x,y,alpha,beta,cam_id,color = 0 , l = 300):
        # render text
        label = self.font.render(str(cam_id), 10, CAMERA)
        self.screen.blit(label, (x+5,y+5))
        # render form
        pygame.draw.circle(self.screen,CAMERA,(x,y),5)
        pygame.draw.line(self.screen,CAMERA,(x,y),(x+l*math.cos(alpha-beta/2),y+l*math.sin(alpha-beta/2)), 2) 
        pygame.draw.line(self.screen,CAMERA,(x,y),(x+l*math.cos(alpha+beta/2),y+l*math.sin(alpha+beta/2)), 2)
        
    def updateScreen(self):
        pygame.display.update() 
     
     
class App:
    def __init__(self,useGUI=1,scenario = 0):
        
        #Here by changing only the vectors it is possbile to create as many scenario as we want !
        if scenario == 0:
            #Options for the target
            self.x_tar = numpy.array([55,270,40,150])
            self.y_tar = numpy.array([55,140,280,150])
            self.vx_tar = numpy.array([0,1,0,0])
            self.vy_tar = numpy.array([0,0,0,0])
            self.size_tar = numpy.array([5,5,5,5])
            self.label_tar = numpy.array(['fix','target','obstruction','fix'])
            #Options for the cameras
            self.x_cam = numpy.array([10,310,10,310,])
            self.y_cam = numpy.array([10,10,310,310])
            self.angle_cam = numpy.array([45,135,315,225])
            self.angle_view_cam = numpy.array([60,60,60,60])
        elif scenario == 1:
            #Options for the target
            self.x_tar = numpy.array([155])
            self.y_tar = numpy.array([40])
            self.vx_tar = numpy.array([0])
            self.vy_tar = numpy.array([0])
            self.size_tar = numpy.array([50])
            self.label_tar = numpy.array(['fix'])
            #Options for the cameras
            self.x_cam = numpy.array([10,310,10,310,])
            self.y_cam = numpy.array([10,10,310,310])
            self.angle_cam = numpy.array([45,135,315,225])
            self.angle_view_cam = numpy.array([60,60,60,60])
            
        
        #Creating the room, the target and the camera
        self.myRoom = Room()
        self.myRoom.createTargets(self.x_tar,self.y_tar,self.vx_tar,self.vy_tar,self.label_tar,self.size_tar)
        self.myRoom.createCameras(self.x_cam,self.y_cam,self.angle_cam,self.angle_view_cam)
        
        #The program can also run complietly with out the GUI interface
        self.useGUI = useGUI
        if useGUI == 1:
            #setting the GUI interface
            self.myGUI = GUI()
            self.updateGUI()  
       
    def main(self):
        while(True): #Boucle d'événements
            #camera is taking a picture
            for camera in self.myRoom.cameras:
                camera.takePicture(self.myRoom.targets)
                
            #Object are moving in the room
            for target in self.myRoom.targets:
                target.mooveTarget(1)
            
            if self.useGUI == 1:
                time.sleep(20) #so that the GUI does go to quick 
                self.updateGUI()
                
        pygame.quit()
           
    def updateGUI(self):
        self.myGUI.drawRoom(self.myRoom.coord)
        
        for target in self.myRoom.targets:
            self.myGUI.drawTarget(target.xc,target.yc,target.size,target.id,target.label,self.myRoom.coord) 
                                           
        for camera in self.myRoom.cameras:    
            self.myGUI.drawCam(camera.xc,camera.yc,camera.alpha,camera.beta,camera.id)
        
        self.myGUI.updateScreen()
        
    

if __name__ == "__main__":
    # execute only if run as a script
    myApp = App(1,1)
    myApp.main()
    