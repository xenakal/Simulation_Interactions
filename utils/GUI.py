class GUI:
    def __init__(self):
        pygame.init()
        #pygame.display.init()
        self.screen = pygame.display.set_mode((640, 960))
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
 