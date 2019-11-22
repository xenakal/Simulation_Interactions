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


def distanceBtwTwoPoint(x1,y1,x2,y2):
           return math.pow(math.pow((x1-x2),2)+math.pow((y1-y2),2),0.5)
        
class Line:
    def __init__(self,x,y,x1,y1):
        self.x = x
        self.y = y
        if(x-x1 == 0):
            self.m = 1
            self.vertical = 1
        else:
            self.m = (y-y1)/(x-x1)
            self.vertical = 0
    
    def linePerp(self,x,y):
        if (self.m == 0):
            return Line(x,y,x,y+1)
        elif(self.vertical == 1):
            return Line(x,y,x+1,y)
        else:
            y1 = (-1/self.m) + y
            return Line(x,y,x+1,y1)
        
    def lineIntersection(self,line):
            if(line.m == self.m):
                return 0
            elif(self.vertical == 1):
                y = line.m*(self.x-line.x)+line.y
                return numpy.array([self.x,y])
            elif(line.vertical == 1):
                y = self.m*(line.x-self.x)+self.y
                return numpy.array([line.x,y]) 
            else:
                x = (line.m*line.x-self.m*self.x-line.y+self.y)/(line.m-self.m)
                y = self.m*(x-self.x)+self.y
                return numpy.array([x,y])
        
    def lineCircleIntersection(self,r,xc,yc):
            if(self.vertical == 1):
                x1 = self.x
                y1 = math.pow((r*r-(self.x-xc)*(self.x-xc)),0.5)+yc
                x2 = self.x
                y2 = -math.pow((r*r-(self.x-xc)*(self.x-xc)),0.5)+yc
            else:
                m = self.m
                xd = self.x
                yd = self.y
                
                a = 1+m*m
                b = -2*xc-2*m*m*xd+2*m*yd-2*m*yc
                c = xc*xc+m*m*xd*xd-2*m*yd*xd+yd*yd+2*m*yc*xd-2*yc*yd+yc*yc-r*r
                
                delta = b*b-4*a*c
            
                x1 = (-b-math.pow(delta,0.5))/(2*a)
                x2 = (-b+math.pow(delta,0.5))/(2*a)
                y1 = m*(x1-self.x)+self.y
                y2 = m*(x2-self.x)+self.y
            
            return numpy.array([x1,y1,x2,y2])
        
    
        
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
        self.projections = []
        
    def takePicture(self,targetList):
        #In first approach to avoid to remove items, list is emptied at the start
        self.targetDetectedList = []
        targetInTriangle = []
        
        #Compute the field seen by the camera
        #alpha, beta are fix now but we could imagine to change alpha, so better to compute it every time.
        m1 = math.sin(self.alpha-self.beta/2)/math.cos(self.alpha-self.beta/2)
        m2 = math.sin(self.alpha+self.beta/2)/math.cos(self.alpha+self.beta/2)
        
        line_cam_1 = Line(self.xc,self.yc,self.xc+math.cos(self.alpha-self.beta/2),self.yc+math.sin(self.alpha-self.beta/2))
        line_cam_2 = Line(self.xc,self.yc,self.xc+math.cos(self.alpha+self.beta/2),self.yc+math.sin(self.alpha+self.beta/2))
        
        #checking for every target if it is in the vision field of the camera.
        for target in targetList:
             #finding the the perpendicular to those line
             line_cam_1_p = line_cam_1.linePerp(target.xc,target.yc)
             line_cam_2_p = line_cam_2.linePerp(target.xc,target.yc)
             #1) finding the perpendicular to the margin crossing the target's center
             #computing the x and y  where the two line intersect 
             i1 = line_cam_1_p.lineIntersection(line_cam_1)
             i2 = line_cam_2_p.lineIntersection(line_cam_2)
             
             d1 = distanceBtwTwoPoint(target.xc,target.yc,i1[0],i1[1])
             d2 = distanceBtwTwoPoint(target.xc,target.yc,i2[0],i2[1])
             
             #2) computing the margin of the view seen by the camera 
             margin_right = ((m1*(target.xc - self.xc) + self.yc)-target.yc)
             margin_left  = ((m2*(target.xc - self.xc) + self.yc)-target.yc)
                 
             #3) checking if the object are in the filed of vision or partially int the field
             if(math.cos(self.alpha+self.beta/2) > 0 and math.cos(self.alpha-self.beta/2) > 0):
                if((margin_right <= 0 and margin_left >= 0) or (( d1 <= target.size or d2 <= target.size) and self.xc < target.xc)):
                    #print("1")
                    targetInTriangle.append(target)
                 
             elif (math.cos(self.alpha+self.beta/2) > 0 and math.cos(self.alpha-self.beta/2) < 0):
                if((margin_right >= 0 and margin_left >= 0) or ((d1 <= target.size or d2 <= target.size) and self.yc > target.yc)):
                    #print("2")
                    targetInTriangle.append(target)
                 
             elif (math.cos(self.alpha+self.beta/2) < 0 and math.cos(self.alpha-self.beta/2) > 0):
                if((margin_right <= 0 and margin_left <= 0) or ((d1 <= target.size or d2 <= target.size) and self.yc < target.yc)):
                    #print("3")
                    targetInTriangle.append(target)
                  
             elif (math.cos(self.alpha+self.beta/2) < 0 and math.cos(self.alpha-self.beta/2) < 0):
                if((margin_right >= 0 and margin_left <= 0) or ((d1 <= target.size or d2 <= target.size)  and self.xc > target.xc)):
                    #print("4")
                    targetInTriangle.append(target)
                    
             elif (math.cos(self.alpha+self.beta/2) > 0 and math.cos(self.alpha-self.beta/2) == 0):
                if((self.xc-targetx < 0 and margin_left <= 0 ) or ((d1 <= target.size or d2 <= target.size) and self.yc > target.yc)):
                    #print("5")
                    targetInTriangle.append(target)
                    
             elif (math.cos(self.alpha+self.beta/2) < 0 and math.cos(self.alpha-self.beta/2) == 0):
                if((self.xc-targetx > 0 and margin_left >= 0) or ((d1 <= target.size or d2 <= target.size) and self.yc < target.yc)):
                    #print("6")
                    targetInTriangle.append(target)
                    
             elif (math.cos(self.alpha+self.beta/2) == 0 and math.cos(self.alpha-self.beta/2) > 0):
                if((self.xc-targetx < 0 and margin_right <= 0) or ((d1 <= target.size or d2 <= target.size) and self.yc < target.yc)):
                    #print("7")
                    targetInTriangle.append(target)
                    
             elif (math.cos(self.alpha+self.beta/2) == 0 and math.cos(self.alpha-self.beta/2) < 0):
                if((self.xc-targetx > 0 and margin_right <= 0) or ((d1 <= target.size or d2 <= target.size) and self.yc > target.yc)):
                    #print("8")
                    targetInTriangle.append(target)
             
        #computation of the distances
        distanceToCam = []
        for target in targetInTriangle:
            distanceToCam.append([math.ceil(distanceBtwTwoPoint(self.xc,self.yc,target.xc,target.yc)),target])
        
        distanceToCam.sort()
        orderedTarget = distanceToCam
        self.projections=[]
        
        #finding the line perpendicular to the median of the camera field to a given distance
        line_cam_median = Line(self.xc,self.yc,self.xc+math.cos(self.alpha),self.yc+math.sin(self.alpha))
        
        idca = line_cam_median.lineCircleIntersection(200,self.xc,self.yc)
        
        if math.cos(self.alpha) < 0:
            xa = idca[0]
            ya = idca[1]
        else:
            xa = idca[2]
            ya = idca[3]
        
        line_cam_median_p = line_cam_median.linePerp(xa,ya)
        self.projections.append(numpy.array([xa,ya,0,0,0]))
        
        #limite of the field of vision on the cmaera
        proj_p1 = line_cam_median_p.lineIntersection(line_cam_1)
        proj_p2 = line_cam_median_p.lineIntersection(line_cam_2)
        self.projections.append(numpy.array([proj_p1[0],proj_p1[1],proj_p2[0],proj_p2[1],0]))
        
        for obj in orderedTarget:
            target = obj[1]
            #line between target and camera     
            line_cam_target = Line(self.xc,self.yc,target.xc,target.yc)   
            #perpendicular
            line_cam_target_p = line_cam_target.linePerp(target.xc,target.yc)
            #intersetion with the target
            idc = line_cam_target_p.lineCircleIntersection(target.size,target.xc,target.yc)
            #line that contains the target
            line_cam_target_1 = Line(self.xc,self.yc,idc[0],idc[1])
            line_cam_target_2 = Line(self.xc,self.yc,idc[2],idc[3])
            #projection of the object on this line
            proj_p1 = line_cam_median_p.lineIntersection(line_cam_target_1)
            proj_p2 = line_cam_median_p.lineIntersection(line_cam_target_2)
            
            #print(distanceBtwTwoPoint(proj_p1[0],proj_p1[1],proj_p2[0],proj_p1[1]))
            
            self.projections.append(numpy.array([proj_p1[0],proj_p1[1],proj_p2[0],proj_p2[1],target.id]))
            #self.projections.append(numpy.array([proj_p2[0],proj_p2[1],proj_p1[0],proj_p1[1]]))
            
        self.targetDetectedList = targetInTriangle
        
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
        
    def drawCam(self,x,y,alpha,beta,cam_id,color = 0 , l = 100):
        # render text
        label = self.font.render(str(cam_id), 10, CAMERA)
        self.screen.blit(label, (x+5,y+5))
        # render form
        pygame.draw.circle(self.screen,CAMERA,(x,y),5)
        pygame.draw.line(self.screen,CAMERA,(x,y),(x+l*math.cos(alpha-beta/2),y+l*math.sin(alpha-beta/2)), 2) 
        pygame.draw.line(self.screen,CAMERA,(x,y),(x+l*math.cos(alpha+beta/2),y+l*math.sin(alpha+beta/2)), 2)
        
    def screenDetectedTarget(self,myRoom):
        
        x_off = 350
        y_off = 50
        color = RED
        
        n = 0 
        for camera in myRoom.cameras:
            label = self.font.render("camera " + str(camera.id), 10, WHITE)
            self.screen.blit(label, (x_off,y_off+n*20))
            n=n+1
        
        n = 0
        label = self.font.render("target ", 10, WHITE)
        self.screen.blit(label, (x_off,y_off-20))
        for target in myRoom.targets:
            label = self.font.render(str(target.id), 10, WHITE)
            self.screen.blit(label, (x_off+80+n*20,y_off-20))
            n=n+1
            
        n = 0
        m = 0 
        for camera in myRoom.cameras:
            n = 0
            for target in myRoom.targets:
                for targetDetected in camera.targetDetectedList:    
                    if target==targetDetected:
                        color = GREEN
                        break
                    else:
                        color = RED
                
                pygame.draw.circle(self.screen,color,(x_off+88+n*20,y_off+7+m*20),5)
                n=n+1
            m =m +1
    
    def drawProjection(self,myRoom):
        x_off = 10
        y_off = 330
        
        pygame.draw.rect(self.screen, BLACK ,(x_off,y_off,500,200))
        
        
        n = 0 
        for camera in myRoom.cameras:
            label = self.font.render("camera " + str(camera.id), 10, WHITE)
            self.screen.blit(label, (x_off,y_off+n*30))
            pygame.draw.circle(self.screen,CAMERA,(x_off + 85 ,y_off+8+n*30),5)
            
            
            m = 0
            for projection in camera.projections:
            
                midle = camera.projections[0]
                #pygame.draw.circle(self.screen,CAMERA,(math.ceil(midle[0]),math.ceil(midle[1])),5)
                ref = camera.projections[1]
                
                if (m>0):
                    d0 = math.floor(distanceBtwTwoPoint(ref[0],ref[1],projection[0],projection[1]))                                       
                    d1 = math.floor(distanceBtwTwoPoint(ref[0],ref[1],projection[2],projection[3]))                                       
                    pygame.draw.circle(self.screen,(100+m*30,255-m*30,255),(x_off + 85 + d0 ,y_off+8+n*30),5)
                    pygame.draw.circle(self.screen,(100+m*30,255-m*30,255),(x_off + 85 + d1 ,y_off+8+n*30),5)
                    
                   
                
                    #pygame.draw.circle(self.screen,(100+n*10,0,0),(math.ceil(projection[0]),math.ceil(projection[1])),5)
                    #pygame.draw.circle(self.screen,(100+n*10,0,0),(math.ceil(projection[2]),math.ceil(projection[3])),5)
                    if (m>1):
                        pygame.draw.line(self.screen,(100+m*30,255-m*30,255),(x_off + 85 + d0,y_off+8+n*30),(x_off+85+d1,y_off+8+n*30), 2)
                        label = self.font.render(str(math.floor(projection[4])), 10, (100+m*30,255-m*30,255))
                        self.screen.blit(label, (x_off + 85 + math.ceil((d0+d1)/2),y_off+10+n*30))
                    
                                                      
                dref = math.floor(distanceBtwTwoPoint(ref[0],ref[1],ref[2],ref[3]))
                pygame.draw.circle(self.screen,WHITE,(x_off + 85 ,y_off+8+n*30),5)
                pygame.draw.circle(self.screen,WHITE,(x_off + 85 + dref,y_off+8+n*30),5)
                m = m+1
            
            n=n+1
                
            
        
    def updateScreen(self):
        pygame.display.update() 
     
     
class App:
    def __init__(self,useGUI=1,scenario = 0):
        
        #Here by changing only the vectors it is possbile to create as many scenario as we want !
        if scenario == 0:
            #Options for the target
            self.x_tar = numpy.array([55,200,40,150])
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
            self.x_tar = numpy.array([150])
            self.y_tar = numpy.array([150])
            self.vx_tar = numpy.array([0])
            self.vy_tar = numpy.array([0])
            self.size_tar = numpy.array([20])
            self.label_tar = numpy.array(['fix'])
            #Options for the cameras
            self.x_cam = numpy.array([10,310,10,310,])
            self.y_cam = numpy.array([10,10,310,310])
            self.angle_cam = numpy.array([45,135,315,225])
            self.angle_view_cam = numpy.array([60,60,60,60])
        elif scenario == 2:
            #Options for the target
            self.x_tar = numpy.array([150,20,50,110])
            self.y_tar = numpy.array([40,20,250,280])
            self.vx_tar = numpy.array([0,0,0,0])
            self.vy_tar = numpy.array([0,0,0,0])
            self.size_tar = numpy.array([30,10,10,15])
            self.label_tar = numpy.array(['fix','fix','fix','fix'])
            #Options for the cameras
            self.x_cam = numpy.array([150])
            self.y_cam = numpy.array([150])
            self.angle_cam = numpy.array([120])
            self.angle_view_cam = numpy.array([60])
            
        
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
                #time.sleep(1) #so that the GUI does go to quick 
                self.updateGUI()
                
        pygame.quit()
           
    def updateGUI(self):
        self.myGUI.drawRoom(self.myRoom.coord)
        
        for target in self.myRoom.targets:
            self.myGUI.drawTarget(target.xc,target.yc,target.size,target.id,target.label,self.myRoom.coord) 
                                           
        for camera in self.myRoom.cameras:    
            self.myGUI.drawCam(camera.xc,camera.yc,camera.alpha,camera.beta,camera.id)
            
        self.myGUI.drawProjection(self.myRoom)
        self.myGUI.screenDetectedTarget(self.myRoom)
        self.myGUI.updateScreen()
        
    
if __name__ == "__main__":
    # execute only if run as a script
    myApp = App(1,0)
    myApp.main()
    