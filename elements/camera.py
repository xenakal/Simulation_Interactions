import math
from utils.line import *
from utils.queueFIFO import *


def avgSpeedFunc(positions):
    if len(positions) <= 1:  # one position or less not enough to calculate speed
        return 0
    prevPos = positions[0]
    stepTime = 1  # TODO: see what the actual time increment is
    avgSpeed = 0.0
    for curPos in positions:
        stepDistance = distanceBtwTwoPoint(prevPos[0], prevPos[1], curPos[0], curPos[1])
        avgSpeed += stepDistance / stepTime
        prevPos = curPos

    avgSpeed = avgSpeed / (len(positions) - 1)
    return avgSpeed


# Returns direction as the angle (in degrees) between the horizontal and the line making the direction
def avgDirectionFunc(positions):
    if len(positions) <= 1:  # one position or less not enough to calculate direction
        return 0
    prevPos = positions[0]
    avgDir = 0
    for curPos in positions:
        edgesRatio = (curPos[1]-prevPos[1]) / (curPos[0]-prevPos[0])  # TODO: check why this gives a warning
        stepDirection = math.asin(edgesRatio)
        avgDir += stepDirection
        prevPos = curPos

    avgDir = avgDir / (len(positions) - 1)
    return avgDir




def calcNextPos(position, speed, direction):
    return 1


class Camera:
    def __init__(self, cam_id, cam_x, cam_y, cam_alpha, cam_beta):
        # Label
        self.id = cam_id
        self.status = 'agent'

        # Location on the map
        self.xc = cam_x
        self.yc = cam_y
        self.alpha = math.radians(cam_alpha)  # deg rotation
        self.beta = math.radians(cam_beta)  # deg view angle

        # Detection
        self.targetDetectedList = []
        self.limitProjection = []

        # Info on targets
        self.previousPositions = dict()  # dictionary where key="target.id" and value="queueFIFO[(x,y)]".
        # not a list as indexes may change if relative positions change

    def takePicture(self, targetList,l_projection = 200,seuil = 3):
        # In first approach to avoid to remove items, list is emptied at the start
        self.targetDetectedList = []
        self.limitProjection = []
        #1)  Finding all the object that are in the triangle 
        targetInTriangle = self.objectsInField(targetList)

        #2) Sort target from the closer to more far away
        orderedTarget = self.sortDetectedTarget(targetInTriangle)
        
        #3) Compute the projection and suppress hidden target
        tab = self.computeProjection(orderedTarget,l_projection,seuil)
        self.limitProjection = tab[0]
        self.targetDetectedList = tab[1]
        
        #4)remember the previous positions of the different targets
        self.updatePreviousPos()  
        
    def objectsInField(self,targetList):
        targetInTriangle = []
        # Compute the field seen by the camera
        line_cam_right = Line(self.xc, self.yc, self.xc + math.cos(self.alpha - self.beta / 2),
                          self.yc + math.sin(self.alpha - self.beta / 2))
        line_cam_left = Line(self.xc, self.yc, self.xc + math.cos(self.alpha + self.beta / 2),
                          self.yc + math.sin(self.alpha + self.beta / 2))
        
        # checking for every target if it is in the vision field of the camera.
        for target in targetList:
            #1) Target cross one of the two line ?
            # finding the perpendicular to the margin crossing the target's center
            line_cam_right_p = line_cam_right.linePerp(target.xc, target.yc)
            line_cam_left_p = line_cam_left.linePerp(target.xc, target.yc)
            # computing the x and y  where the two lines intersect
            i_right = line_cam_right_p.lineIntersection(line_cam_right)
            i_left = line_cam_left_p.lineIntersection(line_cam_left)
            # computing the distances 
            d_right = distanceBtwTwoPoint(target.xc, target.yc, i_right[0], i_right[1])
            d_left = distanceBtwTwoPoint(target.xc, target.yc, i_left[0], i_left[1])
            #If one of those distance is smaller than the target size then the target crosses one the vision limit line
            cdt_object_crossing_bound = (d_right <= target.size or d_left <= target.size)
            object_crossing_bound = 0
            if cdt_object_crossing_bound :
               object_crossing_bound = 1

            # 2) Target center is inside the two line ?
            margin_right = ((line_cam_right.getSlope()[0] * (target.xc - self.xc) + self.yc) - target.yc)
            margin_left = ((line_cam_left.getSlope()[0] * (target.xc - self.xc) + self.yc) - target.yc)

            # 3) Checking both condition for different configuration of the cameras
            targetInTriangle = self.objectsInField_orrientation_cam(targetInTriangle,target,margin_left, margin_right, d_right, d_left,cdt_object_crossing_bound,object_crossing_bound)
        
        return targetInTriangle.copy()

        
    def objectsInField_orrientation_cam(self, targetInTriangle,target,margin_left, margin_right, d1, d2,cdt_object_crossing_bound,object_crossing_bound):
#OTHER POSSIBILITY BUT NOT WORKING YET 
################################################################################################################            
#             alpha_tc = math.atan2((target.yc - self.yc),(target.xc-self.xc))
#             d_cam_target = distanceBtwTwoPoint(target.xc,target.yc,self.xc,self.yc)
#             beta_t  = math.atan2(target.size/2,d_cam_target) #beetwen the center and the border ofthe target
#             
#             if (math.fabs(alpha_tc-self.alpha) < math.fabs(self.beta/2 + beta_t)): #object is seen
#                 object_crossing_bound = 0
#                 if (math.fabs(alpha_tc-self.alpha) > math.fabs(self.beta/2 - beta_t)):
#                    object_crossing_bound = 1
#                 
#                 targetInTriangle.append(numpy.array([target,object_crossing_bound]))
################################################################################################################ 
        
             if(math.cos(self.alpha+self.beta/2) > 0 and math.cos(self.alpha-self.beta/2) > 0):
                if((margin_right <= 0 and margin_left >= 0) or (cdt_object_crossing_bound and self.xc < target.xc)):
                    #print("1")
                    targetInTriangle.append(numpy.array([target,object_crossing_bound]))
                 
             elif (math.cos(self.alpha+self.beta/2) > 0 and math.cos(self.alpha-self.beta/2) < 0):
                if((margin_right >= 0 and margin_left >= 0) or (cdt_object_crossing_bound and self.yc > target.yc)):
                    #print("2")
                    targetInTriangle.append(numpy.array([target,object_crossing_bound]))
                 
             elif (math.cos(self.alpha+self.beta/2) < 0 and math.cos(self.alpha-self.beta/2) > 0):
                if((margin_right <= 0 and margin_left <= 0) or (cdt_object_crossing_bound and self.yc < target.yc)):
                    #print("3")
                    targetInTriangle.append(numpy.array([target,object_crossing_bound]))
                  
             elif (math.cos(self.alpha+self.beta/2) < 0 and math.cos(self.alpha-self.beta/2) < 0):
                if((margin_right >= 0 and margin_left <= 0) or (cdt_object_crossing_bound  and self.xc > target.xc)):
                    #print("4")
                    targetInTriangle.append(numpy.array([target,object_crossing_bound]))
                    
             elif (math.cos(self.alpha+self.beta/2) > 0 and math.cos(self.alpha-self.beta/2) == 0):
                if((self.xc-target.xc < 0 and margin_left <= 0 ) or (cdt_object_crossing_bound and self.yc > target.yc)):
                    #print("5")
                    targetInTriangle.append(numpy.array([target,object_crossing_bound]))
                    
             elif (math.cos(self.alpha+self.beta/2) < 0 and math.cos(self.alpha-self.beta/2) == 0):
                if((self.xc-target.xc > 0 and margin_left >= 0) or (cdt_object_crossing_bound and self.yc < target.yc)):
                    #print("6")
                    targetInTriangle.append(numpy.array([target,object_crossing_bound]))
                    
             elif (math.cos(self.alpha+self.beta/2) == 0 and math.cos(self.alpha-self.beta/2) > 0):
                if((self.xc-target.xc < 0 and margin_right <= 0) or (cdt_object_crossing_bound and self.yc < target.yc)):
                    #print("7")
                    targetInTriangle.append(numpy.array([target,object_crossing_bound]))
                    
             elif (math.cos(self.alpha+self.beta/2) == 0 and math.cos(self.alpha-self.beta/2) < 0):
                if((self.xc-target.xc > 0 and margin_right <= 0) or (cdt_object_crossing_bound and self.yc > target.yc)):
                    #print("8")
                    targetInTriangle.append(numpy.array([target,object_crossing_bound]))

             return targetInTriangle
            
    def sortDetectedTarget(self,targetInTriangle):
        # computation of the distances
        distanceToCam = []
        for target in targetInTriangle:
            distanceToCam.append([math.ceil(distanceBtwTwoPoint(self.xc, self.yc, target[0].xc, target[0].yc)), target])

        distanceToCam.sort()
        return distanceToCam.copy()
    
    
    def computeProjection(self,orderedTarget,l_projection,seuil):
        targeList = []
        proj_cam_view_limit = []
         
        #1) finding the line perpendicular to the median of the camera field to a given distance
        ########################################################################################
        #finding the median 
        line_cam_median = Line(self.xc, self.yc, self.xc + math.cos(self.alpha), self.yc + math.sin(self.alpha))
        # finding the distance l_projection on the line => intersection beetween a line and a circle
        idca = line_cam_median.lineCircleIntersection(l_projection, self.xc, self.yc)
        #two solution 
        if math.cos(self.alpha) < 0:
            xa = idca[0]
            ya = idca[1]
        else:
            xa = idca[2]
            ya = idca[3]
        #finally finding the line
        line_cam_median_p = line_cam_median.linePerp(xa, ya)
        
        #2) projection of the limit
        ############################
        # limit lines of the field of vision on the camera
        line_cam_right = Line(self.xc, self.yc, self.xc + math.cos(self.alpha - self.beta / 2),
                          self.yc + math.sin(self.alpha - self.beta / 2))
        line_cam_left = Line(self.xc, self.yc, self.xc + math.cos(self.alpha + self.beta / 2),
                          self.yc + math.sin(self.alpha + self.beta / 2))

        # projection of the limit of the field of vision on the camera
        ref_proj_p1 = line_cam_median_p.lineIntersection(line_cam_right)
        ref_proj_p2 = line_cam_median_p.lineIntersection(line_cam_left)
        proj_cam_view_limit = numpy.array([ref_proj_p1[0], ref_proj_p1[1], ref_proj_p2[0], ref_proj_p2[1]])
        
        #3) projection of all the targest
        ##################################
        for obj in orderedTarget:
            
            object_crossing_bound = obj[1][1]
            target = obj[1][0]
            hidden = 0
            
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
            #projectio if the object is not hidden
            actuall_projection = numpy.array([proj_p1[0],proj_p1[1],proj_p2[0],proj_p2[1]])
            
            # computing the distance from the left side of the camera
            d2 = distanceBtwTwoPoint(ref_proj_p1[0],ref_proj_p1[1],proj_p1[0],proj_p1[1])
            d3 = distanceBtwTwoPoint(ref_proj_p1[0],ref_proj_p1[1],proj_p2[0],proj_p2[1])
            
            # checking if the point is not in another target thus the camera cannot see it
            for targetAlreadyDetected in self.targetDetectedList:
                
                projection = targetAlreadyDetected[1]
                #if the projection is between two projection then the object cannot be seen by the camera
                d0 = distanceBtwTwoPoint(ref_proj_p1[0],ref_proj_p1[1],projection[0],projection[1])
                d1 = distanceBtwTwoPoint(ref_proj_p1[0],ref_proj_p1[1],projection[2],projection[3])
                
                #condtion to modify the projection seen by the camera
                cdt1 = (d2 < d0 and d2 > d1) #d2 in the middle
                cdt2 = (d2 > d0 and d2 < d1) #d2 in the middle
                cdt3 = (d3 > d0 and d3 < d1) #d3 in the middle
                cdt4 = (d3 < d0 and d3 > d1) #d3 in the middle
                
                cdt5 = (d3 < d0 and d3 < d1 and d0 < d1) #d3 = d0
                cdt6 = (d3 < d0 and d3 < d1 and d0 > d1) #d3 = d1
                cdt7 = (d3 > d0 and d3 > d1 and d0 < d1) #d3 = d1
                cdt8 = (d3 > d0 and d3 > d1 and d0 > d1) #d3 = d0
                
                cdt9 = (d2 < d0 and d2 < d1 and d0 < d1) #d3 = d0
                cdt10 = (d2 < d0 and d2 < d1 and d0 > d1) #d3 = d1
                cdt11 = (d2 > d0 and d2 > d1 and d0 < d1) #d3 = d1
                cdt12 = (d2 > d0 and d2 > d1 and d0 > d1) #d3 = d0
                
                
                #modifying the projection in terms of the conditions
                if((cdt1 or cdt2) and (cdt3 or cdt4)): #
                    #the object is hidden
                    hidden = 2
                    break
                #the object is partially hiden
                elif(cdt1 or cdt2):
                    if(cdt5 or cdt8):
                        proj_p1[0] = projection[0]
                        proj_p1[1] = projection[1]  
                    else:
                        proj_p1[0] = projection[2]
                        proj_p1[1] = projection[3] 
                    hidden = 1
                   
                elif(cdt3 or cdt4):
                    if(cdt9 or cdt12):
                        proj_p2[0] = projection[0]
                        proj_p2[1] = projection[1]   
                    else:
                        proj_p2[0] = projection[2]
                        proj_p2[1] = projection[3] 
                
                    hidden = 1
                    break
                else:
                    #the object is not hidden
                    pass
            
            #saving the new actuall postion 
            actuall_projection = numpy.array([proj_p1[0],proj_p1[1],proj_p2[0],proj_p2[1]])
            #if the taget cross one of the limit of the camera, it is replace by this limit
            if (object_crossing_bound): #target is cut in the camera film
                if(d2 < l_projection*math.tan(self.beta/2) and d3 < l_projection*math.tan(self.beta/2)):
                    actuall_projection = numpy.array([proj_p1[0],proj_p1[1],ref_proj_p1[0],ref_proj_p1[1]])
                else:
                    actuall_projection = numpy.array([ref_proj_p2[0],ref_proj_p2[1],proj_p2[0],proj_p2[1]])    
            #if the taget is not complietely hidden then it added      
            if (hidden == 0 or hidden == 1 and distanceBtwTwoPoint(proj_p1[0],proj_p1[1],proj_p2[0],proj_p2[1]) > seuil):
                targeList.append(numpy.array([target,actuall_projection,hidden]))
                
        
        return numpy.array([proj_cam_view_limit,targeList])

    def updatePreviousPos(self):
        for targetObj in self.targetDetectedList:
            if targetObj[0].id not in self.previousPositions:
                self.previousPositions[targetObj[0].id] = QueueFIFO()  # create new entry in dict
            self.previousPositions[targetObj[0].id].enqueue([targetObj[0].xc, targetObj[0].yc])  # update dict

    def predictPaths(self):
        for targetObj in self.targetDetectedList:
            self.predictPath(targetObj[0])

    def predictPath(self, target):
        #  We have access to the real speeds, but in the real application we won't, therefore we have to approximate.
        prevPositions = self.previousPositions[target.id].getQueue()
        #  Calculate average velocity
        avgSpeed = avgSpeedFunc(prevPositions)
        #  Calculate average direction
        avgDirection = avgDirectionFunc(prevPositions)
        #  Use avg velocity and direction to estimate next position
        nextPositions = calcNextPos(prevPositions[0], avgSpeed, avgDirection)
        return nextPositions

    def analysePicture(self):
        print('analysing picture')

    def sendMessageToCam(self):
        print('sending message')

    def writeOnTheWhiteBoard(self):
        print('writting on the white board')
