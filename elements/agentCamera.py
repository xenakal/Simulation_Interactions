import threading
import mailbox
import time
import logging
import numpy as np
from elements.agent import*
from elements.target import*
from utils.infoAgentCamera import*
from utils.message import*

NAME_MAILBOX = "mailbox/MailBox_Agent"
        
class AgentCam(Agent):
    def __init__(self,idAgent,camera,room):
        #Attributes
        self.cam = camera
        self.memory = InformationMemory(20)
        
        #log_room
        logger_room = logging.getLogger('room'+str(idAgent))
        logger_room.setLevel(logging.INFO)
        # create file handler which log_messages even debug messages
        fh = logging.FileHandler(NAME_LOG_PATH+str(idAgent)+"-room","w+")
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log_message level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger_message
        logger_room.addHandler(fh)
        logger_room.addHandler(ch)
        
        self.log_room = logger_room
        
        super().__init__(idAgent,room)
        
           
    def thread_processImage(self):
        state = "takePicture"
        nextstate = state
    
        my_time = self.myRoom.time
        my_previousTime = my_time-1
         
        picture = []
        while(self.threadRun == 1):
            
            state = nextstate
            my_time = self.myRoom.time
            
            if state == "takePicture":
                picture = self.cam.takePicture(self.myRoom.targets)
                
                #if the room dispositon has evolve we create a new table
                if(my_previousTime != my_time):
                    my_previousTime = my_time
                    self.updateMemory("newPicture",picture)
                    s = self.memory.memoryToString()
                    self.log_room.info(s)
                    nextstate = "makePrediction" # Avoir si on peut améliorer les prédictions avec les mes recu
                else:
                    nextstate = "processData"
             
             
            elif state == "makePrediction":
                #Prediction based on a picture
                prediction = self.cam.predictPaths()
                nextstate = "processData"
              
              
            elif nextstate == "processData":
                #Prediction based on messages
                #All the message a written based on the value of my_time
                self.processInfoMemory(my_time)
                nextstate = "sendMessage"
            
            
            elif state == "sendMessage":
                cdt1 = self.info_messageSent.getSize() > 0
                cdt2 = self.info_messageReceived.getSize()> 0
                cdt3 = self.info_messageToSend.getSize()> 0
                
                if(cdt1 or cdt2 or cdt3):
                    pass
                    #self.log_room.info(self.info_messageSent.printMyList())
                    #self.log_room.info(self.info_messageReceived.printMyList())
                    #self.log_room.info(self.info_messageToSend.printMyList())
                
                self.info_messageSent.removeMessageAfterGivenTime(my_time,10)
                self.info_messageReceived.removeMessageAfterGivenTime(my_time,10)
                self.sendAllMessage()
                
                if MULTI_THREAD != 1:
                        self.recAllMess()
                        self.processRecMess()
                else:
                    time.sleep(0.2)
                
                nextstate = "takePicture"
                
            else:
                print("FSM not working proerly")
           
    #################################
    #   Store and process information
    ################################# 
    def updateMemory(self,type_update,objet):    
        #create a new colums in the table to save the information of the picture  
        if(type_update == "newPicture"):
            # copy the information from last time, all the target unseen
            self.memory.addNewTime(self.myRoom.time)
            picture = objet
            #adding all the target seen
            for elem in picture:
                #When added from the previous time value
                #The target is by default unseen
                #If it is seen in the picture this line changes the value
                self.memory.addTarget(self.myRoom.time,elem[0])
                self.memory.setSeenByCam(self.myRoom.time,elem[0],True) # set that the target is seen
            
        #modify the information of the message     
        elif(type_update == "infoFromOtherCam"):
            pass    
        else:
            pass

    
    #define what message to send in terms of the info store in memory
    def processInfoMemory(self,time):
        #IMPORTANT we can decide on which time we base the message we send
        for info in  self.memory.info_room[self.memory.computeIndexBasedOnTime(time)]: 
            if info.target.label == "target":
                #if the cam sees the object and the object is not followed by an ohter cam    
                if info.seenByCam and info.followedByCam == -1:
                    #Then send a request to follow this target
                    #Also signal to other cam that this target exit
                    dx = self.cam.xc-info.target.xc
                    dy = self.cam.yc-info.target.yc
                    distance = math.pow(dx*dx+dy*dy,0.5)
                    self.sendMessageType('request',distance,True,info.target.id)
                    
            elif info.target.label == "obstruction":
                pass
            elif info.target.label == "fix":
                pass
                 

    def processRecMess(self):
        for rec_mes in self.info_messageReceived.getList():
            
            if(rec_mes.messageType == "request"):
                #Update Info
                self.updateMemory("infoFromOtherCam",rec_mes)
                rep_mes = rec_mes
                
                typeMessage="ack"
                if self.memory.isTargetDetected(self.myRoom.time,rec_mes.targetRef):
                #If the target is seen => distances # AJouté la condition
                    #if(distance < distance 2)
                        #typeMessage="ack"
                    #else:
                    typeMessage="nack"   
                else:
                #If the target is not seen then ACK
                    typeMessage ="ack"
                    
                self.sendMessageType(typeMessage,rep_mes,False)
                #self.info_messageReceived.delMessage(rec_mes)
            
            elif(rec_mes.messageType == "ack" or rec_mes.messageType == "nack"):
                for mes_sent in self.info_messageSent.getList():
                    added = mes_sent.add_ACK_NACK(rec_mes)
                    if added:
                        self.info_messageReceived.delMessage(rec_mes)
                        if mes_sent.is_approved():
                            self.memory.setfollowedByCam(self.myRoom.time,mes_sent.targetRef,self.id)
                            #should take the message
                            #should send a aquire
                            pass #print("all Ack received") #do some stuff
                        elif mes_sent.is_not_approved():
                            pass #do some stuff
                        break
                    
            elif(rec_mes.messageType == "heartbeat"):
                pass

            else:
                pass
    
            #message supress from the wainting list
            
            #self.info_messageReceived.delMessage(rec_mes)
    
  
        
if __name__ == "__main__":
    pass
 
    
    
    
