import threading
import mailbox
import time
import numpy as np
from elements.target import*


class InformationTable:
    def __init__(self, cameras, targets, nTime = 1):
        self.times = range(0,nTime)
        self.cameras = cameras
        self.targets = targets
     
        self.info = self.initInfo()
        #print(self.info)
        
       
    def initInfo(self):
        #target is the target we are looking
        #seenByCam tells if that target is currently seen (0 = No 1 = YES)
        #camIncharge tells which cam is in charge of tracking that object (-1 is the init value)
        #distance is the distance between the target and the cam (-1 is the init value)
        #time is the instance from which the information is from
        infoType = [('target', Target),('seenByCam',int),('camInCharge',int),('distance', int),('time',int)]
        info = []
        for time in self.times:
            for camera in self.cameras:
                for targets in self.targets:
                    info.append((Target(),0,-1,-1,time))
        
        return np.array(info, dtype=infoType)
    
    #should delete the last time and add a new colone for the new time
    def updateInfo(self,target,t):
        pass
    
    def modifyInfo(self,target,camera,t):
         pass
    
        
class AgentCam:
    def __init__(self, idAgent,camera,room):
        #Attributes
        self.id = idAgent
        self.cam = camera
        self.myRoom = room
        self.tableau = InformationTable(self.myRoom.cameras,self.myRoom.targets,10)
        
        #Communication
        self.mbox = mailbox.mbox('agent'+str(idAgent))
        self.mbox.clear()
        
        #Threads
        self.threadRun = 1
        self.thread_pI = threading.Thread(target=self.thread_processImage,args=(self.myRoom,)) #,daemon=True)
        self.thread_rL = threading.Thread(target=self.thread_recLoop) #,daemon=True)
        threading.Timer(1,self.thread_processImage)
        threading.Timer(1,self.thread_recLoop)
        
        
        self.run()
    
    def run(self):
        self.thread_pI.start()
        self.thread_rL.start()
         
        #self.thread_pI.join()
        #self.thread_rL.join()

    def thread_processImage(self,myRoom):
        state = "takePicture"
        nextstate = state
        while(self.threadRun == 1):
            
            state = nextstate
            
            if state == "takePicture":
                picture = self.cam.takePicture(myRoom.targets)
                #self.tableau.updateInfo(self,target,myRoom.t)
                nextstate = "makePrediction"
                
            elif state == "makePrediction":
                prediction = self.cam.predictPaths()
                #d'autre prédiction peuvent être réalisées à cette étape
                nextstate = "sendMessage"
                
            elif state == "sendMessage":
                #Base on the prediction we can decide what we would send
                self.defineWhomToSend("Hello ",myRoom)
                nextstate = "takePicture"
                time.sleep(0.2)
            else:
                print("FSM not working proerly")
            
            
    def thread_recLoop(self):
        while(self.threadRun == 1):
            self.recMess()
            #self.tableau.modifyInfo(self,target,camera,t):
                
    def defineWhomToSend(self,m,myRoom):
        #Different tags can be use
        
        #A) ACTION BASED ON WHAT THE CAMERA SEES
        #New target detected
            #1) check if already followed by a camera  ?
                #YES ---> checking if we have a better view
                    #YES ---> sending a message
                    #NO finish
        
                #NO  send a request to the other cam
                for agent in myRoom.agentCam:
                    if(agent.id != self.id):
                        self.sendMess(m +str(agent.id),agent.id)
            
        #B) ACTION BASED ON WHAT THE CAMERA CAN PREDICTE
        #target will be hidden / leave the field of the camera
            #analyse(prediction) --> tags
            #1) check if a camera has also a view
                #YES ---> tell the camera to follow it
                    
                #NO  ----> sending a message to the user to inform that the target is no more followed7
    
    def parseRecMess(self,m):
        print(m)
        return 0
    
    #la fonction renvoie -1 quand les messages n'ont pas été lu
    def recMess(self):
        succes = -1
        #Reading the message 
        mbox_rec = mailbox.mbox('agent'+str(self.id))
        try:
            mbox_rec.lock()
            keys = mbox_rec.keys()
            is_ACK_NACK = 0
            try:
                for key in keys:
                    is_ACK_NACK = 0 
                    m = mbox_rec.get_string(key)
                    
                    if (m != ""):  
                          is_ACK_NACK = self.parseRecMess(m) 
                          mbox_rec.remove(key)
                          mbox_rec.flush()
            finally:
                mbox_rec.unlock()
                
                #Sending a ACK or NACK
                sender_ID = 0 #should be in the message
                if(is_ACK_NACK == "ACK"):
                    message = "Ack ..."
                    succes = self.sendMess(self, message, sender_ID)
                elif(is_ACK_NACK == "NACK"):
                    succes = message = "Nack ..."
                    self.sendMess(self, message, sender_ID)
                                        
        except mailbox.ExternalClashError:
            pass
            #print("not possible to read the message")
        except FileExistsError:
            pass
            #print("file does not exist ??")
            
    
    #la fonction renvoie -1 quand le message n'a pas été envoyé mais ne s'occupe pas de le réenvoyer ! 
    def sendMess(self, m, receiverID):
        succes = -1
        try: 
            mbox = mailbox.mbox('agent'+str(receiverID))
            mbox.lock()
            try:
                key = mbox.add("Agent"+str(self.id)+":"+m)
                mbox.flush()
                succes = 0
                #print("message sent successfully")   
            finally:
                mbox.unlock()
        except mailbox.ExternalClashError:
            pass
            #message not sent
            #print("not possible to send the message")
        except FileExistsError:
            pass
            #print("file does not exist ??")
        return succes
    
    def writeLog(self, message):
        return 'agent '+str(self.id)+' '+message
    
    #J'ai pas encore trouvé comment faire ça de façon propre
    def clear(self):
        self.threadRun = 0
        while(self.thread_pI.is_alive() and self.thread_pI.is_alive()):
            pass
        self.mbox.close()
  
        
if __name__ == "__main__":
    pass
 
    
    
    
