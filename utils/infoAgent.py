import numpy as np
import random

class TargetInfos():
    def __init__(self,timeStamp, target, followedByCam = -1,cam  = -1,distance = -1):
        self.timeStamp = timeStamp
        self.target = target
        self.seenByCam_and_distance = [(cam,distance)]
        self.followedByCam =  followedByCam
        #self.ack_received = 0
        #self.nack_received = 0
        

class Message():
    def __init__(self,timeStamp,senderID, receiverID, messageType,message):
        self.senderID = senderID
        self.receiverID = receiverID
        self.message = message
        self.messageType = messageType
        self.timeStamp = timeStamp
        self.specialNumber = random.random() * 10000000000000000
        self.formatMessageType()

    def modifyMessageFromString(self,s):
        att = s.split("-")
        self.senderID = att[2]
        self.receiverID = att[3]
        self.message = att[5]
        self.messageType = att[4]
        self.timeStamp = att[1]
        self.specialNumber = float(att[0])
        self.formatMessageType()
        
    def formatMessageType(self):
        base =  str(self.specialNumber)+'-'+ str(self.timeStamp)+'-'+str(self.senderID)+'-'+str(self.receiverID)+'-'+str(self.messageType)
        if self.messageType == 'request' or self.messageType == 'request_all':
            message = "target" + '_' + str(self.message)
        elif self.messageType == 'ack' or self.messageType == 'nack':
            message = self.message
        elif self.messageType == 'information':
            message = self.message
        elif self.messageType == 'information':
            message = self.message
        else:
            message = ""
            
        return base +'-'+ message
    
    def parseMessageType(self):
        if self.messageType == 'request' or self.messageType == 'request_all':
            att = self.message.split('_')
            message = att[1]  #information utile 
        elif self.messageType == 'ack' or self.messageType == 'nack':
            message = self.message
        elif self.messageType == 'information':
            message = self.message
        elif self.messageType == 'information':
            message = self.message
        else:
            message = self.message
            
        return message
        
    def printMessage(self):
        return 'message #'+str(self.specialNumber)+' - time :' + str(self.timeStamp) + '- from agent :'+str(self.senderID)+' - to agent :'+str(self.receiverID)+' - '+self.messageType + ' - '+str(self.message)
        
        
class ListMessage():
    def __init__(self,name):
        self.myList = []
        self.name = name
        
    def getList(self):
        return self.myList.copy()
    
    def addMessage(self,message):
        self.myList.append(message)
        
    def delMessage(self,message):
        self.myList.remove(message)
    
    def findMessage(self,message):
        pass #à implémenter
    
    def printMyList(self):
        s = self.name + "\n"
        for message in self.myList:
            s = s + message.printMessage() +  "\n"
        
        return s
    
class InformationTable:
    def __init__(self, cameras, targets, nTime = 5):
        self.times = nTime
        self.cameras = cameras
        self.targets = targets
    
        self.info_room =  []
        
        #List to know what has been send, receive and what could be process
        #A implémenter dans la classe agentCamera, à chaque fois qu'un message est envoyé il est ajouté
        # recu idem, puis une fonction parcours pour voir si il y a un match en les recus et les envoyés
        #Si c'est le cas suppression dens liste d'attente et ajout lié dans la liste des informations traitable
        self.info_messageSent = ListMessage("Sent")
        self.info_messageReceived = ListMessage("Received")
        self.info_messageToSend = ListMessage("ToSend")
        
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
                    
if __name__ == "__main__":
    pass
   
    
    