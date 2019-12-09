import threading
import mailbox
import time
import logging
import numpy as np
from elements.target import*
from utils.message import*

NAME_LOG_PATH = "log/log_agent/Agent"
NAME_MAILBOX = "mailbox/MailBox_Agent"
MULTI_THREAD = 0 
        
class Agent:
    def __init__(self,idAgent,room):
        #Attributes
        self.id = idAgent
        self.myRoom = room
        self.signature = int(random.random() * 10000000000000000)+100 #always higher than 100
        
        #Communication
        self.info_messageSent = ListMessage("Sent")
        self.info_messageReceived = ListMessage("Received")
        self.info_messageToSend = ListMessage("ToSend")
        
        self.mbox = mailbox.mbox(NAME_MAILBOX+str(self.id))
        self.mbox.clear()
        
        #Threads
        self.threadRun = 1
        self.thread_pI = threading.Thread(target=self.thread_processImage) 
        self.thread_rL = threading.Thread(target=self.thread_recLoop)
        threading.Timer(1,self.thread_processImage)
        threading.Timer(1,self.thread_recLoop)
        
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
        state = "processData"
        nextstate = state
    
        my_time = self.myRoom.time
        my_previousTime = my_time-1
         
        picture = []
        while(self.threadRun == 1):
            
            state = nextstate
            my_time = self.myRoom.time
              
            if nextstate == "processData":
                #Prediction based on messages
                self.processInfoMemory()
                nextstate = "sendMessage"
            
            
            elif state == "sendMessage": 
                self.sendAllMessage()
                
                if MULTI_THREAD != 1:
                        self.recAllMess()
                        self.processRecMess()
                else:
                    time.sleep(0.2)
                
                nextstate = "processData"
                
            else:
                print("FSM not working proerly")
            
            
    def thread_recLoop(self):
        while(self.threadRun == 1):
            self.recAllMess()
            self.processRecMess()
            
           
    ############################
    #   Store and process information
    ############################  
    def updateTable(self,type_update,objet):    
       pass
    
    #define what message to send in terms of the info store in memory
    def processInfoMemory(self):
       pass
    
    #Save informations and if needed prepare a response            
    def processRecMess(self):
        pass
            
    ############################
    #   Receive Information
    ############################
    def parseRecMess(self,m):
        #reconstruction de l'objet message
        rec_mes = Message(0,0,0,0,0)
        rec_mes.modifyMessageFromString(m)
        
        self.info_messageReceived.addMessage(rec_mes)
        self.log_message.info('RECEIVED : \n'+ rec_mes.formatMessageType())
    
    
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
        for message in self.info_messageToSend.getList():
            isSend = self.sendMess(message)
            if isSend == 0:
                    self.info_messageToSend.delMessage(message)
                    self.info_messageSent.addMessage(message)
            
    
    #la fonction renvoie -1 quand le message n'a pas été envoyé mais ne s'occupe pas de le réenvoyer ! 
    def sendMess(self, m):
        succes = -1
        
        for receiver in m.remainingReceiver:
            try: 
                mbox = mailbox.mbox(NAME_MAILBOX+str(receiver[0]))
                mbox.lock()
                try:
                    mbox.add(m.formatMessageType()) #apparament on ne peut pas transférer d'objet
                    self.log_message.info('SEND     : \n'+m.formatMessageType())
                    mbox.flush()
                    m.notifySendTo(receiver[0],receiver[1])
                    
                    if m.isMessageSentToEveryReceiver():
                        succes = 0
                    else:
                        succes = 1 #message partially sent
                finally:
                    mbox.unlock()
        
            ##############################
                if MULTI_THREAD != 1:
                    pass
                    #Agentreceive.recAllMess()
                    #Agentreceive.processRecMess()
            ##############################
                            
            except mailbox.ExternalClashError:
                self.log_message.debug("Not possible to send messages")
            except FileExistsError:
                self.log_message.warning("Mailbox file error SEND")
            
        return succes
    
    
    def sendMessageType(self,typeMessage,m,to_all=False,target =-1, receiverID_Signature=-1):
        m_format = Message(-1,-1,-1,'init',"")
        
        if(typeMessage == "request"):
            m_format = Message(self.myRoom.time,self.id,self.signature,typeMessage,m,target)
        
        elif(typeMessage == "wanted"):
            m_format = Message(self.myRoom.time,self.id,self.signature,typeMessage,m,target)
        
        elif(typeMessage == "locked"):
            m_format = Message(self.myRoom.time,self.id,self.signature,typeMessage,m.signature,m.targetRef)
            to_all=True
                            
        elif(typeMessage == "ack"):
            m_format = Message(self.myRoom.time,self.id,self.signature,typeMessage,m.signature,m.targetRef)
            m_format.addReceiver(m.senderID,m.senderSignature)
            to_all=False 
                            
        elif(typeMessage == "nack"):
            m_format = Message(self.myRoom.time,self.id,self.signature,typeMessage,m.signature,m.targetRef)
            m_format.addReceiver(m.senderID,m.senderSignature)
            to_all=False
                            
        elif(typeMessage == "heartbeat"):
            m_format = Message(self.myRoom.time,self.id,self.signature,typeMessage,"heartbeat",target)
        
        if to_all:
            for agent in self.myRoom.agentCam:
                if(agent.id != self.id):
                    m_format.addReceiver(agent.id,agent.signature)
            
        
        cdt1 = m_format.getReceiverNumber() > 0
        cdt2 = self.info_messageToSend.isMessageWithSameTypeSameAgentRef(m_format)
        cdt3 = self.info_messageSent.isMessageWithSameTypeSameAgentRef(m_format)
        if  cdt1 and not cdt2 and not cdt3 : 
            self.info_messageToSend.addMessage(m_format)
            
    ############################
    # Other
    ############################
    
    
    def clear(self):
        self.threadRun = 0
        while(self.thread_pI.is_alive() and self.thread_pI.is_alive()):
            pass
        self.mbox.close()
  
        
if __name__ == "__main__":
    pass
 
    
    
    

