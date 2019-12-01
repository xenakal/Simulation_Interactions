import numpy as np

class InformationTable:
    def __init__(self, cameras = 3 , targets = 3, nTime = 10):
        self.times = range(0,nTime)
        self.cameras =range(0,cameras)
        self.targets =range(0,targets)
    
        self.info = self.initInfo()
        #print(self.info)
        
       
    def initInfo(self):
        #target is the target we are looking
        #seenByCam tells if that target is currently seen (0 = No 1 = YES)
        #camIncharge tells which cam is in charge of tracking that object (-1 is the init value)
        #distance is the distance between the target and the cam (-1 is the init value)
        #time is the instance from which the information is from
        infoType = [('time',int),('cam',int),('target', int),('seenByCam',int),('camInCharge',int),('distance', int)]
        info = []
        timeTab = []
        
        for time in self.times:
            for camera in self.cameras:
                for target in self.targets:
                    timeTab.append((time,target,camera,-1,-1,-1))
            
            np.array(timeTab, dtype=infoType)
            info.append(timeTab)
            timeTab = []
            
        
        return info
    
    #should delete the last time and add a new colone for the new time
    def updateInfo(self,time):
        del self.info[0]
        timeTab = []
        for camera in self.cameras:
                for target in self.targets:
                    timeTab.append((time,target,camera,-1,-1,-1))
                    
        self.info.append(timeTab)
            
    
    
    
    def modifyInfo(self,target,camera,t):
         pass
        
if __name__ == "__main__":
    table = InformationTable()
    print(table.info[0])