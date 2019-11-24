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
        
    
