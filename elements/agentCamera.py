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
        self.table = InformationTable(room.cameras,room.targets,20)
        
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
                    self.updateTable("newPicture",picture)
                    s = self.table.printFieldRoom()
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
                self.processInfoMemory()
                nextstate = "sendMessage"
            
            
            elif state == "sendMessage":
                cdt1 = self.info_messageSent.getSize() > 0
                cdt2 = self.info_messageReceived.getSize()> 0
                cdt3 = self.info_messageToSend.getSize()> 0
                
                if(cdt1 or cdt2 or cdt3):
                    self.log_room.info(self.info_messageSent.printMyList())
                    self.log_room.info(self.info_messageReceived.printMyList())
                    self.log_room.info(self.info_messageToSend.printMyList())
                
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
    def updateTable(self,type_update,objet):    
        #create a new colums in the table to save the information of the picture  
        if(type_update == "newPicture"):
            picture = objet
            targets = []
            for elem in picture:
                targets.append(elem[0])
                
            self.table.updateInfoRoom(self.myRoom.time,targets,self.cam,-1)
            
        #modify the information of the message     
        elif(type_update == "infoFromOtherCam"):
            pass    
        else:
            pass

    
    #define what message to send in terms of the info store in memory
    def processInfoMemory(self):
        if(self.myRoom.time < 12):
                    self.sendMessageType('request',1,True,0,0) 
                    
#            if actual_target.label == "target":
#                pass
#            elif actual_target.label == "obstruction":
#                pass
#            elif actual_target.label == "fix":
#                pass
                 
            #1) check if already followed by a camera  ?
                #YES ---> checking if we have a better view
                    #YES ---> sending a message
                    #NO finish
        
                #NO  send a request to the other cam
                
            
        #B) ACTION BASED ON WHAT THE CAMERA CAN PREDICTE
        #target will be hidden / leave the field of the camera
            #analyse(prediction) --> tags
            #1) check if a camera has also a view
                #YES ---> tell the camera to follow it
                    
                #NO  ----> sending a message to the user to inform that the target is no more followed
        
         #Save informations and if needed prepare a response            

    def processRecMess(self):
        for rec_mes in self.info_messageReceived.getList():
            
            if(rec_mes.messageType == "request"):
                #Update Info
                self.updateTable("infoFromOtherCam",rec_mes)
                            
                rep_mes = rec_mes
                if self.table.isTargetDetected(rec_mes.parseMessageType()):
                    #If the target is seen => distances # AJouté la condition
                    #if(distance < distance 2)
                        typeMessage="ack"
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
                    self.info_messageReceived.delMessage(rec_mes)
                    if added:
                        if mes_sent.is_approved():
                            print("all Ack received") #do some stuff
                        elif mes_sent.is_not_Approved():
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
 
    
    
    
