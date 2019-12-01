import threading
import mailbox
import time
import logging
import numpy as np
from elements.target import*
from utils.infoAgent import*

NAME_MAILBOX = "mailbox/MailBox_Agent"
NAME_LOG_PATH = "log/log_agent/Agent"

        
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
        self.thread_pI = threading.Thread(target=self.thread_processImage) #,daemon=True)
        self.thread_rL = threading.Thread(target=self.thread_recLoop) #,daemon=True)
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
        self.thread_rL.start()
         
        #self.thread_pI.join()
        #self.thread_rL.join()

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
                    self.updateTable(my_time,"newPicture",picture)
                    s = self.table.printFieldRoom()
                    self.log_room.info(s)
                    
                nextstate = "makePrediction"
                
            elif state == "makePrediction":
                prediction = self.cam.predictPaths()
                #d'autre prédiction peuvent être réalisées à cette étape
                nextstate = "sendMessage"
                
            elif state == "sendMessage":
                #Base on the prediction we can decide what we would send
                self.defineWhomToSendWhat(my_time,picture)
                nextstate = "takePicture"
                time.sleep(0.2)
            else:
                print("FSM not working proerly")
            
            
    def thread_recLoop(self):
        while(self.threadRun == 1):
            self.recMess()
            #self.tableau.modifyInfo(self,target,camera,t):
            #self.updateTable(picture,prediction)
            
    def updateTable(self,time,type_update,picture):    
        #create a new colums in the table to save the information of the picture  
        if(type_update == "newPicture"):
            targets = []
            for elem in picture:
                targets.append(elem[0])
            self.table.updateInfoRoom(time,targets,self.cam,-1)
            
        #modify the information of the message     
        elif(type_update == "newPicture"):
            pass
        else:
            pass

                
    def defineWhomToSendWhat(self,time,picture):
        #Different tags can be use
        for elem in picture:
            actual_target = elem[0]
        #A) ACTION BASED ON WHAT THE CAMERA SEES
        #New target detected
            if actual_target.label == "target":
                
                #critère à modifier sur le fait qu'un message à déjà été envoyé
                isDetected = self.table.wasTargetAlreadyDeteced(actual_target)
                if(not isDetected):
                    self.sendMessageType(time,"request",0,actual_target,"")
                    
                        
            elif actual_target.label == "obstruction":
                pass
            elif actual_target.label == "fix":
                pass
            else:
                print("In agentCamera, defineWhomToSend : wrong label chosen")
            
                
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
    
    def sendMessageType(self,time, typeMessage, reiceiverID , target , m):
        
        if(typeMessage == "request"):
            for agent in self.myRoom.agentCam:
                        if(agent.id != self.id):
                            m = Message(time,self.id,agent.id,typeMessage,"target"+str(target.id))
                            self.sendMess(m)
                            
        elif(typeMessage == "ack"):
            m = Message(time,self.id,m.senderID,typeMessage,m.message)
            self.sendMess(m)
                            
        elif(typeMessage == "nack"):
            m = Message(time,self.id,m.senderID,typeMessage,m.message)
            self.sendMess(m)
                            
        elif(typeMessage == "heartbeat"):
            m = Message(time,self.id,receiverID,typeMessage,m)
            self.sendMess(m)
                            
        elif(typeMessage == "information"):
            m = Message(time,self.id,agent.id,typeMessage,message)
            self.sendMess(m)
                            
    
    def parseRecMess(self,m):
        #print(m)
        self.log_message.info('RECEIVED : '+ m)
        return 0
    
    def recMess(self):
        succes = -1
        #Reading the message 
        mbox_rec = mailbox.mbox(NAME_MAILBOX+str(self.id))
        try:
            mbox_rec.lock()
            keys = mbox_rec.keys()
            try:
                for key in keys: 
                    m = mbox_rec.get_string(key)
                    
                    if (m != ""):  
                          needToReply = self.parseRecMess(m)
                          
                          #Sending a ACK or NACK
                          if(needToReply  == 1):
                             succes = self.sendMess(self, message, sender_ID)
                            
                          if (succes == 0): #if we respond then the message is remove from the mail box   
                             mbox_rec.remove(key)
                             mbox_rec.flush()
            finally:
                mbox_rec.unlock()
            
            
        except mailbox.ExternalClashError:
            self.log_message.debug("Not possible to read messages")
        except FileExistsError:
            self.log_message.warning("Mailbox file error")
        
        return succes
            
    
    #la fonction renvoie -1 quand le message n'a pas été envoyé mais ne s'occupe pas de le réenvoyer ! 
    def sendMess(self, m):
        succes = -1
        try: 
            mbox = mailbox.mbox(NAME_MAILBOX+str(m.receiverID))
            mbox.lock()
            try:
                mbox.add(m.printMessage()) #apparament on ne peut pas transférer d'objet
                self.log_message.info(m.printMessage())
                mbox.flush()
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
            self.log_message.warning("Mailbox file error")
            
        return succes
    
    #J'ai pas encore trouvé comment faire ça de façon propre
    def clear(self):
        self.threadRun = 0
        while(self.thread_pI.is_alive() and self.thread_pI.is_alive()):
            pass
        self.mbox.close()
  
        
if __name__ == "__main__":
    pass
 
    
    
    
