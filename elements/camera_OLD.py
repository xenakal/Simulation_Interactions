import math
import main
import numpy as np
from utils.line import *
from utils.queueFIFO import *
from elements.target import *

NUMBER_PREDICTIONS = 3


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
    counter = 0
    for curPos in positions[1:]:
        dy = curPos[1] - prevPos[1]
        dx = curPos[0] - prevPos[0]
        stepDirection = math.atan2(float(dy), float(dx))
        avgDir += stepDirection

        prevPos = curPos
        counter += 1

    avgDir = avgDir / counter
    #  print("avgDir " + str(avgDir))
    return avgDir


def calcNextPos(position, speed, direction):
    travelDistance = main.TIMESTEP * 4 * speed
    xPrediction = position[0] + math.cos(direction) * travelDistance
    yPrediction = position[1] + math.sin(direction) * travelDistance  # -: the coordinates are opposite to the cartesian
    return [int(xPrediction), int(yPrediction)]


class Camera:
    def __init__(self, cam_id, cam_x, cam_y, cam_alpha, cam_beta, fix=1):
        # Label
        self.id = cam_id
        self.status = 'agent'
        self.isActive = 1

        # Location on the map
        self.xc = cam_x
        self.yc = cam_y
        self.alpha = math.radians(cam_alpha)  # deg rotation
        self.beta = math.radians(cam_beta)  # deg view angle
        self.fix = fix

        # Detection
        self.targetDetectedList = []
        self.limitProjection = []

        # Info on targets
        self.previousPositions = dict()  # dictionary where key="target" and value="queueFIFO[(x,y)]".
        # not a list as indexes may change if relative positions change
        self.predictedPositions = dict()  # key="target" and value=queueFIFO([predicted_xc, predicted_yc])

    def run(self, myRoom):
        if self.isActive == 1:
            self.takePicture(myRoom.targets)
            self.predictPaths()

    def camDesactivate(self):
        self.isActive = 0

    def camActivate(self):
        self.isActive = 1

    def isActivate(self):
        if self.isActive == 1:
            return True
        else:
            return False

    def takePicture(self, targetList, l_projection=200, seuil=3):
        if self.isActive == 1:
            # In first approach to avoid to remove items, list is emptied at the start
            self.targetDetectedList = []  # list containing target objects
            self.limitProjection = []
            # 1)  Finding all the objects that are in the triangle
            targetInTriangle = self.objectsInField(targetList)

            # 2) Sort target from the closer to more far away
            orderedTarget = self.sortDetectedTarget(targetInTriangle)

            # 3) Compute the projection and suppress hidden target
            tab = self.computeProjection(orderedTarget, l_projection, seuil)
            self.limitProjection = tab[0]
            self.targetDetectedList = tab[1]  # [target objects, position, hidden]

            # 4)remember the previous positions of the different targets
            self.updatePreviousPos()

            # 5) if the camera is not fix it can rotate
            self.cam_rotate(math.radians(1))

            return tab[1].copy()

    def coord_from_WorldFrame_to_CamFrame(self, x, y):
        xi = x - self.xc
        yi = y - self.yc

        xf = math.cos(self.alpha) * xi + math.sin(self.alpha) * yi
        yf = -math.sin(self.alpha) * xi + math.cos(self.alpha) * yi
        return numpy.array([xf, yf])

    def objectsInField(self, targetList):
        self.targetDetectedList = []
        targetInTriangle = []
        # Compute the field seen by the camera
        line_cam_right = Line(self.xc, self.yc, self.xc + math.cos(self.alpha - self.beta / 2),
                              self.yc + math.sin(self.alpha - self.beta / 2))
        line_cam_left = Line(self.xc, self.yc, self.xc + math.cos(self.alpha + self.beta / 2),
                             self.yc + math.sin(self.alpha + self.beta / 2))

        # checking for every target if it is in the vision field of the camera.
        for target in targetList:
            # Frame transformation from the world frame to the cam frame for each target
            coord_cam_frame = self.coord_from_WorldFrame_to_CamFrame(target.xc, target.yc)
            alpha_target_camFrame = math.atan2(coord_cam_frame[1], coord_cam_frame[0])
            d_cam_target = distanceBtwTwoPoint(coord_cam_frame[0], coord_cam_frame[1], 0, 0)
            beta_target = math.atan2(target.size / 2, d_cam_target)  # between the center and the border of the target

            margin_high = alpha_target_camFrame <= math.fabs(self.beta / 2) + math.fabs(beta_target)
            margin_low = alpha_target_camFrame >= -(math.fabs(self.beta / 2) + math.fabs(beta_target))

            if margin_low and margin_high:  # object is seen
                # print('object id: '+str(target.id))
                # print(math.degrees(alpha_target_camFrame))
                # print(coord_cam_frame)
                # print(math.degrees(self.beta/2))
                # print(math.degrees(beta_target))
                # print(math.degrees(alpha_target_camFrame))
                targetInTriangle.append(target)

        return targetInTriangle.copy()

    def sortDetectedTarget(self, targetInTriangle):
        # computation of the distances
        distanceToCam = []
        orderedTarget = []

        for target in targetInTriangle:
            distanceToCam.append((math.ceil(distanceBtwTwoPoint(self.xc, self.yc, target.xc, target.yc)), target))

        dtype = [('distance', int), ('target', Target)]
        a = np.array(distanceToCam, dtype=dtype)

        try:
            a = np.sort(a, axis=0, order='distance')
        except TypeError:
            print("something went wrong with cam (unable to sort): " + str(self.id))
        except SystemError:
            pass

        # keeping just the target
        for element in a:
            orderedTarget.append(element['target'])

        return orderedTarget

    def computeProjection(self, orderedTarget, l_projection, seuil):
        targetList = []
        proj_cam_view_limit = []

        #        #IN CAM FRAME
        #        #finding the two limits
        #
        #        line_cam_left = Line(0,0,math.cos(self.beta/2),math.sin(self.beta / 2))
        #        line_cam_right = Line(0,0,math.cos(self.beta/2),-math.sin(self.beta/2))
        #        line_projection = Line(l_projection,0,l_projection,2)
        #
        #        ref_proj_left_cam_frame = line_projection.lineIntersection(line_cam_left)
        #        ref_proj_right_cam_frame = line_projection.lineIntersection(line_cam_right)
        #
        #        for target in orderedTarget:
        #
        #            coord_cam_frame = self.coord_from_WorldFrame_to_CamFrame(target.xc,target.yc)
        #            #line between target and camera
        #            line_cam_target = Line(0,0,coord_cam_frame[0],coord_cam_frame[1])
        #            line_cam_target_p = line_cam_target.linePerp(coord_cam_frame[0],coord_cam_frame[1])
        #            #intersetion with the target
        #            idc = line_cam_target_p.lineCircleIntersection(target.size,coord_cam_frame[0],coord_cam_frame[1])
        #            #line that contains the target
        #            line_cam_target_left = Line(0,0,idc[0],idc[1])
        #            line_cam_target_right = Line(0,0,idc[2],idc[3])
        #            #projection of the object on this line
        #            proj_left_cam_frame = line_projection.lineIntersection(line_cam_target_left)
        #            proj_pright_cam_frame = line_projection.lineIntersection(line_cam_target_right)
        #
        #            if(proj_left_cam_frame[1] <= proj_pright_cam_frame[1]):
        #                print("ok")

        # 1) finding the line perpendicular to the median of the camera field to a given distance
        ########################################################################################
        # finding the median
        line_cam_median = Line(self.xc, self.yc, self.xc + math.cos(self.alpha), self.yc + math.sin(self.alpha))
        # finding the distance l_projection on the line => intersection beetween a line and a circle
        idca = line_cam_median.lineCircleIntersection(l_projection, self.xc, self.yc)
        # two solutions
        if math.cos(self.alpha) <= 0 or self.alpha == math.pi / 2:
            xa = idca[0]
            ya = idca[1]
        else:
            xa = idca[2]
            ya = idca[3]
            # finally finding the line
        line_cam_median_p = line_cam_median.linePerp(xa, ya)

        # 2) projection of the limit
        ############################
        # limit lines of the field of vision on the camera
        line_cam_right = Line(self.xc, self.yc, self.xc + math.cos(self.alpha - self.beta / 2),
                              self.yc + math.sin(self.alpha - self.beta / 2))
        line_cam_left = Line(self.xc, self.yc, self.xc + math.cos(self.alpha + self.beta / 2),
                             self.yc + math.sin(self.alpha + self.beta / 2))
        # projection of the limit of the field of vision on the camera
        ref_proj_left = line_cam_median_p.lineIntersection(line_cam_left)
        ref_proj_right = line_cam_median_p.lineIntersection(line_cam_right)
        # projection in cam frame
        ref_proj_left_cam_frame = self.coord_from_WorldFrame_to_CamFrame(ref_proj_left[0], ref_proj_left[1])
        ref_proj_right_cam_frame = self.coord_from_WorldFrame_to_CamFrame(ref_proj_right[0], ref_proj_right[1])

        proj_cam_view_limit = numpy.array([ref_proj_left[0], ref_proj_left[1], ref_proj_right[0], ref_proj_right[1]])

        # 3) projection of all the targets
        ##################################
        for target in orderedTarget:
            hidden = 0

            # line between target and camera
            line_cam_target = Line(self.xc, self.yc, target.xc, target.yc)
            # perpendicular
            line_cam_target_p = line_cam_target.linePerp(target.xc, target.yc)
            # intersetion with the target
            idc = line_cam_target_p.lineCircleIntersection(target.size, target.xc, target.yc)
            # line that contains the target
            line_cam_target_1 = Line(self.xc, self.yc, idc[0], idc[1])
            line_cam_target_2 = Line(self.xc, self.yc, idc[2], idc[3])
            # projection of the object on this line
            proj_p1 = line_cam_median_p.lineIntersection(line_cam_target_1)
            proj_p2 = line_cam_median_p.lineIntersection(line_cam_target_2)
            # projection in cam frame
            proj_p1_cam_frame = self.coord_from_WorldFrame_to_CamFrame(proj_p1[0], proj_p1[1])
            proj_p2_cam_frame = self.coord_from_WorldFrame_to_CamFrame(proj_p2[0], proj_p2[1])

            # projection if the object is not hidden
            actual_projection_worldFrame = numpy.array([proj_p1[0], proj_p1[1], proj_p2[0], proj_p2[1]])

            # computing the distance from the left side of the camera
            d0 = distanceBtwTwoPoint(ref_proj_left[0], ref_proj_left[1], proj_p1[0], proj_p1[1])
            d1 = distanceBtwTwoPoint(ref_proj_left[0], ref_proj_left[1], proj_p2[0], proj_p2[1])
            # checking if the point is not in another target thus the camera cannot see it
            for targetAlreadyDetected in targetList:
                projection = targetAlreadyDetected[1]

                # X = lprojection due to the frame transformation thus we can focus on y

                # if the projection is between two projection then the object cannot be seen by the camera
                d2 = distanceBtwTwoPoint(ref_proj_left[0], ref_proj_left[1], projection[0], projection[1])
                d3 = distanceBtwTwoPoint(ref_proj_left[0], ref_proj_left[1], projection[2], projection[3])

                # condition to modify the projection seen by the camera
                cdt1 = (d2 > d0 > d3)  # d0 in the middle
                cdt2 = (d2 < d0 < d3)  # d0 in the middle
                cdt3 = (d2 < d1 < d3)  # d1 in the middle
                cdt4 = (d2 > d1 > d3)  # d1 in the middle

                cdt5 = (d1 < d2 < d3 and d1 < d3)  # d1 = d2
                cdt6 = (d1 < d2 and d1 < d3 < d2)  # d1 = d3
                cdt7 = (d1 > d2 and d1 > d3 > d2)  # d1 = d3
                cdt8 = (d1 > d2 > d3 and d1 > d3)  # d1 = d2

                cdt9 = (d0 < d2 < d3 and d0 < d3)  # d1 = d2
                cdt10 = (d0 < d2 and d0 < d3 < d2)  # d1 = d3
                cdt11 = (d0 > d2 and d0 > d3 > d2)  # d1 = d3
                cdt12 = (d0 > d2 > d3 and d0 > d3)  # d1 = d2

                # modifying the projection in terms of the conditions
                if (cdt1 or cdt2) and (cdt3 or cdt4):  #
                    # the object is hidden
                    hidden = 2
                    break
                # the object is partially hidden
                elif cdt1 or cdt2:
                    if cdt5 or cdt8:
                        proj_p1[0] = projection[0]
                        proj_p1[1] = projection[1]
                    else:
                        proj_p1[0] = projection[2]
                        proj_p1[1] = projection[3]
                    hidden = 1

                elif cdt3 or cdt4:
                    if cdt9 or cdt12:
                        proj_p2[0] = projection[0]
                        proj_p2[1] = projection[1]
                    else:
                        proj_p2[0] = projection[2]
                        proj_p2[1] = projection[3]

                    hidden = 1
                    break
                else:
                    # the object is not hidden
                    pass

            # checking if the target is outside from the camera bound
            # print(target.id)
            # print(proj_p1_cam_frame[1])
            # print(proj_p2_cam_frame[1])
            # print(ref_proj_left_cam_frame)
            # print(ref_proj_right_cam_frame)

            if proj_p1_cam_frame[1] < ref_proj_right_cam_frame[1] and proj_p1_cam_frame[1] < 0:
                proj_p1[0] = ref_proj_right[0]
                proj_p1[1] = ref_proj_right[1]
            if proj_p1_cam_frame[1] > ref_proj_left_cam_frame[1] and proj_p1_cam_frame[1] > 0:
                proj_p1[0] = ref_proj_left[0]
                proj_p1[1] = ref_proj_left[1]
            if proj_p2_cam_frame[1] < ref_proj_right_cam_frame[1] and proj_p2_cam_frame[1] < 0:
                proj_p2[0] = ref_proj_right[0]
                proj_p2[1] = ref_proj_right[1]
            if proj_p2_cam_frame[1] > ref_proj_left_cam_frame[1] and proj_p2_cam_frame[1] > 0:
                proj_p2[0] = ref_proj_left[0]
                proj_p2[1] = ref_proj_left[1]

            # saving the new actual position
            actual_projection_worldFrame = numpy.array([proj_p1[0], proj_p1[1], proj_p2[0], proj_p2[1]])

            # if the target is not completely hidden then it added
            if ((hidden == 0 or hidden == 1) and distanceBtwTwoPoint(proj_p1[0], proj_p1[1], proj_p2[0],
                                                                     proj_p2[1]) > seuil):
                targetList.append(numpy.array([target, actual_projection_worldFrame, hidden]))

        return numpy.array([proj_cam_view_limit, targetList])

    def cam_rotate(self, step):
        if self.fix == 0:
            self.alpha = self.alpha + step

    #  This method will return bullshit predictions if object disappears and reappears elsewhere
    def updatePreviousPos(self):
        for target in self.targetDetectedList:
            targetObj = target[0]  # target object
            if targetObj.label == 'target':
                if targetObj not in self.previousPositions:  # not encountered the object yet
                    self.previousPositions[targetObj] = QueueFIFO()  # create new entry in dict
                self.previousPositions[targetObj].enqueue([targetObj.xc, targetObj.yc])  # update dict

    #  Predict the paths of all targets previously seen as a list with the NUMBER_PREDICTIONS next estimated positions
    def predictPaths(self):
        for targetObj in self.previousPositions:
            self.predictedPositions[targetObj] = self.nextPositions(targetObj)

    def nextPositions(self, target):
        predictedPos = [None] * NUMBER_PREDICTIONS
        #  We have access to the real speeds, but in the real application we won't, therefore we have to approximate
        prevPos = self.previousPositions[target].getQueue()
        currPos = [target.xc, target.yc]

        for i in range(NUMBER_PREDICTIONS):
            #  Estimate next position
            avgSpeed = avgSpeedFunc(prevPos)  # calculate average velocity
            avgDirection = avgDirectionFunc(prevPos)  # calculate average direction
            nextPos = calcNextPos(currPos, avgSpeed, avgDirection)  # estimate next position
            predictedPos[i] = nextPos
            # Update needed values
            prevPos = prevPos[1:]  # include new pos for next iteration
            prevPos.append(currPos)
            currPos = nextPos

        return predictedPos
