import numpy as np
import random

class TargetInfos():
    def __init__(self,timeStamp, targetID, followedByCam = -1,seenByCam  = False,distance = -1):
        self.timeStamp = timeStamp
        self.targetID = targetID
        self.seenByCam = seenByCam
        self.distance = distance
        self.followedByCam =  followedByCam
    
    def copyTargetInfo_newTime(self,time):
        return TargetInfos(time,self.targetID,self.followedByCam,self.seenByCam,self.distance)
               
    def setTimeStamp(self,time):
        self.timeStamp = time
    
class InformationMemory:
    def __init__(self, nTime = 5,currentTime = 0):
        self.times = nTime
        self.currentTime = currentTime
        self.info_room =[]    
    
    def computeIndexBasedOnTime(self,infoTime):
        if infoTime > self.currentTime - len(self.info_room)-1:
            if len(self.info_room) > 0:
                return (len(self.info_room) - 1) - (self.currentTime - infoTime)
            else:
                return 0
          
    def addNewTime(self,time):
        self.currentTime = time
        n = len(self.info_room)
        timeTab = []
        if n > 0:
            for element in self.info_room[n-1]:
                timeTab.append(element.copyTargetInfo_newTime(time))
                
        if n > self.times-1:
            del self.info_room[0]
            
        self.info_room.append(timeTab)
    
        
    def addTarget(self,infoTime,targetID):
        index = self.computeIndexBasedOnTime(infoTime)
        for element in self.info_room[index]:
            if element.targetID == targetID:
                return False
    
        self.info_room[index].append(TargetInfos(infoTime,targetID))
        return True
         
    def updateTarget_info(self,infoTime,targetID,camInCharge,camera,distance):
        index =  computeIndexBasedOnTime(infoTime)
        info_index = self.info_room[index]
        for info in info_index:
            if(info.targetID == targetID):
                info_index.seenByCam=camera
                info_index.distance = distance
                info_index.followedByCam = camInCharge
                break
    
    def isTargetDetected(self,infoTime,targetID):
        index = computeIndexBasedOnTime(infoTime)
        info_index = self.info_room[index]
        for info in info_index:
            if(info.targetID == targetID):
                if(info.seenByCam):
                    return True    
        return False
    
    def wasTargetAlreadyDeteced(self,targetID):
        size = len(self.info_room) 
        if (size > 0):
            info_index = self.info_room[size-2]
            for info in info_index:
                if(info.targetID == targetID):
                    return True
        return False
    
    def getCamInCharge(self,infoTime,targetID):
        index = computeIndexBasedOnTime(infoTime)
        for info in self.info_room[index]:
            if(info.targetID == targetID):
                return info.followedByCam
    
   
    
    
    def memoryToString(self):
        s ="Memory \n"
        
        for timeStamp in self.info_room:
                for info in timeStamp:
                    s = s + ("time : " + str(info.timeStamp) + " target " + str(info.targetID) +"\n")
            
        return s
            
                    
if __name__ == "__main__":
    memory = InformationMemory(3)
    print(memory.memoryToString())
    
    memory.addNewTime(1)
    memory.addTarget(1,"test")
    memory.addTarget(1,"test1")
    print(memory.memoryToString())
    
    memory.addNewTime(2)
    print(memory.memoryToString())
    memory.addNewTime(3)
    print(memory.memoryToString())
    memory.addNewTime(4)
    print(memory.memoryToString())
    memory.addNewTime(5)
    print(memory.memoryToString())
    
    
   
    
    