import threading
import mailbox
import time
import logging
import numpy as np
from elements.target import*
from utils.infoAgent import*

NAME_MAILBOX = "mailbox/MailBox_Agent"
NAME_LOG_PATH = "log/log_agent/Agent"

MULTI_THREAD = 0 
        
class AgentCam:
    def __init__(self, idAgent,camera,room):
        #Attributes
        self.id = idAgent
        self.cam = camera
        self.myRoom = room
        self.table = InformationTable(self.myRoom.cameras,self.myRoom.targets,10)
        
        #Communication
        self.mbox = mailbox.mbox(NAME_MAILBOX+str(idAgent))
        self.mbox.clear()
        
        #Threads
        self.threadRun = 1
        self.thread_pI = threading.Thread(target=self.thread_processImage) 
        self.thread_rL = threading.Thread(target=self.thread_recLoop)
        threading.Timer(1,self.thread_processImage)
        threading.Timer(1,self.thread_recLoop)
        
        #log_room
        logger_room = logging.getLogger('room'+str(self.id))
        logger_room.setLevel(logging.INFO)
        # create file handler which log_messages even debug messages
        fh = logging.FileHandler(NAME_LOG_PATH+str(self.id)+"-room","w+")
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
        
        #log_message
        # create logger_message with 'spam_application'
        logger_message = logging.getLogger('agent'+str(self.id))
        logger_message.setLevel(logging.INFO)
        # create file handler which log_messages even debug messages
        fh = logging.FileHandler(NAME_LOG_PATH+str(self.id)+"-messages","w+")
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log_message level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger_message
        logger_message.addHandler(fh)
        logger_message.addHandler(ch)
        
        self.log_message = logger_message
        
        #Startrun()
        self.run()
        self.log_message.info('Agent initialized and  starts')
        
    def run(self):
        self.thread_pI.start()
        if MULTI_THREAD == 1:
            self.thread_rL.start()

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
                self.log_room.info(self.table.info_messageSent.printMyList())
                self.log_room.info(self.table.info_messageReceived.printMyList())
                self.log_room.info(self.table.info_messageToSend.printMyList())
                
                self.sendAllMessage()
                
                if MULTI_THREAD != 1:
                        self.recAllMess()
                        self.processRecMess()
                else:
                    time.sleep(0.2)
                
                nextstate = "takePicture"
                
            else:
                print("FSM not working proerly")
            
            
    def thread_recLoop(self):
        while(self.threadRun == 1):
            self.recAllMess()
            self.processRecMess()
            #self.tableau.modifyInfo(self,target,camera,t):
            #self.updateTable(picture,prediction)
            
           
    ############################
    #   Stor and process information
    ############################  
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
        #Different tags can be use
        if(self.myRoom.time < 1):
                    self.sendMessageType('request_all',0)
                    
                    
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
        for rec_mes in self.table.info_messageReceived.getList():
            if(rec_mes.messageType == "request_all" or rec_mes.messageType == "request"):
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
            
            elif(rec_mes.messageType == "ack" or rec_mes.messageType == "nack"):
                rep_mes = -1
            elif(rec_mes.messageType == "information"):
                pass
            elif(rec_mes.messageType == "heartbeat"):
                pass
            else:
                pass
    
            if(rep_mes !=-1):
                self.sendMessageType(typeMessage,rep_mes,rec_mes.receiverID)
            
            #message supress from the wainting list
            self.table.info_messageReceived.delMessage(rec_mes)
                
            
    #Ici il faut faire enc sorte d'etre sur que le message à été envoyé parce qu'il se peut qu'il ne soit pas du tout envoyé 
    def sendMessageType(self,typeMessage,m,receiverID=0):
        if(typeMessage == "request_all"):
            for agent in self.myRoom.agentCam:
                        if(agent.id != self.id):
                            m = Message(self.myRoom.time,self.id,agent.id,typeMessage,m) #ici il faut aussi transmettre la distance
                            self.table.info_messageToSend.addMessage(m)

        elif(typeMessage == "request"):
            m = Message(self.myRoom.time,self.id,receiverID,typeMessage,m) #ici il faut aussi transmettre la distance
                            
        elif(typeMessage == "ack"):
            m = Message(self.myRoom.time,self.id,m.senderID,typeMessage,m.formatMessageType())
                            
        elif(typeMessage == "nack"):
            m = Message(self.myRoom.time,self.id,m.senderID,typeMessage,m.formatMessageType())
                            
        elif(typeMessage == "heartbeat"):
            m = Message(self.myRoom.time,self.id,receiverID,typeMessage,"heartbeat")
                            
        elif(typeMessage == "information"):
            m = Message(self.myRoom.time,self.id,receiverID,typeMessage,"what ever for now")
        
        else:
            m = -1
            
        if m != -1 and typeMessage !=  'request_all':
            self.table.info_messageToSend.addMessage(m)
            
    ############################
    #   Receive Information
    ############################
    def parseRecMess(self,m):
        #reconstruction de l'objet message
        rec_mes = Message(0,0,0,0,0)
        rec_mes.modifyMessageFromString(m)
        
        self.table.info_messageReceived.addMessage(rec_mes)
        self.log_message.info('RECEIVED : '+ rec_mes.printMessage())
    
    
    def recAllMess(self):
        succes = -1
        #Reading the message 
        mbox_rec = mailbox.mbox(NAME_MAILBOX+str(self.id))
        try:
            mbox_rec.lock()
            keys = mbox_rec.keys()
            try:
                succes = 0 
                for key in keys: 
                    m = mbox_rec.get_string(key)
                    
                    if (m != ""):  
                          self.parseRecMess(m) #We put the message in the stack of received message BUT not response !
                          
                          if (succes == 0): #if we respond then the message is remove from the mail box   
                             mbox_rec.remove(key)
                             mbox_rec.flush()
            finally:
                mbox_rec.unlock()
            
            
        except mailbox.ExternalClashError:
            self.log_message.debug("Not possible to read messages")
        except FileExistsError:
            self.log_message.warning("Mailbox file error RECEIVE")
        
        return succes
      
    ############################
    #   Send Information
    ############################  
    def sendAllMessage(self):
        for message in self.table.info_messageToSend.getList():
            isSend = self.sendMess(message)
            if isSend == 0:
                    self.table.info_messageToSend.delMessage(message)
                    self.table.info_messageSent.addMessage(message)
            
    
    #la fonction renvoie -1 quand le message n'a pas été envoyé mais ne s'occupe pas de le réenvoyer ! 
    def sendMess(self, m):
        succes = -1
        try: 
            mbox = mailbox.mbox(NAME_MAILBOX+str(m.receiverID))
            mbox.lock()
            try:
                mbox.add(m.formatMessageType()) #apparament on ne peut pas transférer d'objet
                self.log_message.info('SEND     : '+m.printMessage())
                mbox.flush()
                
                #saving the message in a data base to remember it was sent
                #self.table.addMessageSend()
            
                succes = 0
                #print("message sent successfully")   
            finally:
                mbox.unlock()
                
        ##############################
                
            #1) on choppe la ref de l'agent à qui on envoie
            #refAgent = getRef()
            #refAgent.recMess()
                
        ##############################
            
        except mailbox.ExternalClashError:
            self.log_message.debug("Not possible to send messages")
        except FileExistsError:
            self.log_message.warning("Mailbox file error SEND")
            
        return succes
    
    #J'ai pas encore trouvé comment faire ça de façon propre
    def clear(self):
        self.threadRun = 0
        while(self.thread_pI.is_alive() and self.thread_pI.is_alive()):
            pass
        self.mbox.close()
  
        
if __name__ == "__main__":
    pass
 
    
    
    
