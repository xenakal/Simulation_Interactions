import numpy as np
import random

class Message():
    def __init__(self,timeStamp,senderID, receiverID, messageType,message):
        self.senderID = senderID
        self.receiverID = receiverID
        self.message = message
        self.messageType = messageType
        self.timeStamp = timeStamp
        self.specialNumber = random.random() * 10000000000000000

     
    def simpleFormatMessage(self):
        return str(self.timeStamp)+'-'+str(self.senderID)+'-'+str(self.receiverID)+'-'+self.messageType + '-' +self.message +'-'+str(self.specialNumber)
        
    def printMessage(self):
        return 'message #'+str(self.specialNumber)+' - time :' + str(self.timeStamp) + '- from agent :'+str(self.senderID)+' - to agent :'+str(self.receiverID)+' - '+self.messageType + ' - ' +self.message    
    
    def setSpecialNumber(self,s):
        self.specialNumber = s
    
class TargetInfos():
    def __init__(self,timeStamp, target, followedByCam = -1,cam  = -1,distance = -1):
        self.timeStamp = timeStamp
        self.target = target
        self.seenByCam_and_distance = [(cam,distance)]
        self.followedByCam =  followedByCam
        self.ack_received = 0
        self.nack_received = 0
    
    
class InformationTable:
    def __init__(self, cameras, targets, nTime = 5):
        self.times = nTime
        self.cameras = cameras
        self.targets = targets
    
        self.info_room =  [] #self.initInfo()
        self.info_message = self.initInfoMessage()
        #print(self.info_room
    
    def initInfoMessage(self):
        info_message = []
        for camera in self.cameras:
            info_cam = []
            for camera in self.cameras:
                info_cam.append([])
            info_message.append(info_cam)
                
        return info_message
        
    
    def updateInfoRoom(self,time,targetDetected,cam ,distance):
        if len(self.info_room) >= self.times:
            del self.info_room[0]
            
        timeTab = []
        for target in targetDetected:
            followedByCam = -1 
            if len(self.info_room) >= 1:
               followedByCam = self.getInfoRoomCamInCharge
               
            timeTab.append(TargetInfos(time,target,followedByCam,cam,distance))
                    
        self.info_room.append(timeTab)
        
    def updateInfoRoomField(self,index,target,camInCharge,camera,distance):
        info_index = self.info_room[index]
        for info in info_index:
            if(info.target.id == target.id):
                info_index.seenByCam_and_distance.append(camera,distance)
                info_index.followedByCam = camInCharge
                info_index.distance = distance
                break
            
    def getInfoRoomCamInCharge(self,index,target):
        info_index = self.info_room[index]
        for info in info_index:
            if(info.target.id == target.id):
                return info_index.followedByCam
            
    def isTargetDetected(self,targetID):
        info_index = self.info_room[len(self.info_room)-1]
        
        for info in info_index:
            if(info.target.id == targetID):
                return True
            
        return False
    
    def wasTargetAlreadyDeteced(self,target):
        size = len(self.info_room) 
        if (size > 0):
            info_index = self.info_room[size-2]
            for info in info_index:
                if(info.target.id == target.id):
                    return True
        return False  
            
    def printFieldRoom(self):
        s = ""
        for n in  range(0,len(self.info_room)-1):
            for info in self.info_room[n]:
                s = s + ("time : " + str(info.timeStamp) + " target " + str(info.target.id) +"\n")
                
        return s     
                    
    def addInfoMessage(self,camSenderID,camReceiverID,message):
        n = 0
        m = 0
        
        for camera in self.cameras:
            if camera.id == camSenderID:
                break
            else:
                n = n + 1
                
        for camera in self.cameras:
            if camera.id == camReceiverID:
                break
            else:
                m = m + 1
        try:
            self.info_message[n][m].append(message)
        except IndexError:
            print(str(n)+","+str(m) + " // sender :" + str(camSenderID) + " --> receiver :" + str(camReceiverID) + " // num : " + str(message.specialNumber))
            print("ERREUR :not abble to store message ?????")         
        
    def remInfoMessage(self,camSenderID,camReceiverIDmessage):
        n = 0
        m = 0
        
        for camera in self.cameras:
            if camera.id == camSenderID:
                break
            else:
                n = n + 1
                
        for camera in self.cameras:
            if camera.id == camReceiverID:
                break
            else:
                m = m + 1
        try:
            self.info_message[n][m].append(message)
        except IndexError:
            print(str(n)+","+str(m) + " // sender :" + str(camSenderID) + " --> receiver :" + str(camReceiverID) + " // num : " + str(message.specialNumber))
            print("ERREUR :not abble to delete message ?????")    

    
#    def checkMessageInInfoMessage(self,message):
#        for n in range(0,len(self.cameras)-1):
#            for m in range(0,len(self.cameras)-1):
#                for savedMessage in self.info_message[n][m]:
#                    if message.specialNumber == savedMessage.specialNumber:
#                        return True
#                    
#        return False
        
if __name__ == "__main__":
   table = InformationTable(0,1,2)
   print(table.info_message)
    
    