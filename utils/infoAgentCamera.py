import numpy as np
import random

class TargetInfos():
    def __init__(self,timeStamp, target,seenByCam=False,followedByCam=-1,distance=-1):
        self.timeStamp = timeStamp
        self.target = target
        self.seenByCam = seenByCam
        self.distance = distance
        self.followedByCam =  followedByCam
    
    def copyTargetInfo_newTime(self,time,seenByCam):
        return TargetInfos(time,self.target,seenByCam,self.followedByCam,self.distance)
    
    def setTargetFromID(self,targetID,myRoom):
        for target in myRoom.targets:
            if(str(target.id) == str(targetID)):
                self.target = target
                return True
        return False
               
    def setTimeStamp(self,time):
        self.timeStamp = time
    
    def setSeenByCam(self,setter):
        self.seenByCam = setter
    
class InformationMemory:
    def __init__(self, nTime = 5,currentTime = 0):
        self.times = nTime
        self.currentTime = currentTime
        self.info_room =[]    
    
    def computeIndexBasedOnTime(self,infoTime):
        if infoTime > self.currentTime - len(self.info_room)-1:
            if len(self.info_room) > 0:
                return (len(self.info_room)-1)-(self.currentTime - infoTime)
            else:
                return 0
          
    def addNewTime(self,time):
        self.currentTime = time
        n = len(self.info_room)
        timeTab = []
        if n > 0:
            for element in self.info_room[n-1]:
                timeTab.append(element.copyTargetInfo_newTime(time,False))
                
        if n > self.times-1:
            del self.info_room[0]
            
        self.info_room.append(timeTab)
    
        
    def addTarget(self,infoTime,target):
        index = self.computeIndexBasedOnTime(infoTime)
        for element in self.info_room[index]:
            if element.target.id == target.id:
                return False #if already in the list
            
        self.info_room[index].append(TargetInfos(infoTime,target)) 
        return True #otherwise add it
    
    def addTargetFromID(self,infoTime,targetID,myRoom):
        index = self.computeIndexBasedOnTime(infoTime)
        
        try:
            info_index = self.info_room[index]
        except IndexError:
            print("error")
            info_index = self.info_room[len(self.info_room)-1]
            
        for element in info_index :
            if element.target.id == targetID:
                return False #if already in the list
         
        newTar = TargetInfos(infoTime,targetID)
        test = newTar.setTargetFromID(targetID,myRoom)
        info_index.append(newTar) 
        return True #otherwise add it
         
    def updateTarget_info(self,infoTime,target,camInCharge,camera,distance):
        index =  computeIndexBasedOnTime(infoTime)
        
        try:
            info_index = self.info_room[index]
        except IndexError:
            print("error")
            info_index = self.info_room[len(self.info_room)-1]
        
        
        for info in info_index:
            if(info.target.id == target.id):
                info_index.seenByCam=camera
                info_index.distance = distance
                info_index.followedByCam = camInCharge
                break
    
    def isTargetDetected(self,infoTime,targetID):
        index = self.computeIndexBasedOnTime(infoTime)
       
        try:
            info_index = self.info_room[index]
        except IndexError:
            print("error")
            info_index = self.info_room[len(self.info_room)-1]
            
        for info in info_index:
            if(info.target.id == targetID):
                if(info.seenByCam):
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
    
    def setSeenByCam(self,infoTime,target,setter):
        index = self.computeIndexBasedOnTime(infoTime)
        
        try:
            info_index = self.info_room[index]
        except IndexError:
            print("error")
            info_index = self.info_room[len(self.info_room)-1]
            
        for info in self.info_room[index]:
            if(info.target.id == target.id):
                info.setSeenByCam(True)
                return True
        return false
    
    def setfollowedByCam(self,infoTime,targetID,agentID):
        index = self.computeIndexBasedOnTime(infoTime)
        
        try:
            info_index = self.info_room[index]
        except IndexError:
            print("error")
            info_index = self.info_room[len(self.info_room)-1]
        
        for info in info_index:
            if str(info.target.id) == str(targetID):
                info.followedByCam = agentID
                return True
        return False
    
    
    def getCamInCharge(self,infoTime,target):
        index = computeIndexBasedOnTime(infoTime)
        for info in self.info_room[index]:
            if(info.target.id == target.id):
                return info.followedByCam
   
    
    
    def memoryToString(self):
        s ="Memory \n"
        
        for timeStamp in self.info_room:
                for info in timeStamp:
                    s1 ="time : " + str(info.timeStamp) + " target " + str(info.target.id)  
                    s2 =" seen : " + str(info.seenByCam) + " lock : " + str(info.followedByCam) + "\n"
                    s = s + s1 + s2
            
        return s
            
                    
if __name__ == "__main__":
   pass
    
    
   
    
    