import threading
import mailbox
import time
from elements.target import *
from elements.camera import *

TARGET0 = 25 
TARGET1 = 26

class Agent:
    def __init__(self, idAgent):
        self.id = idAgent
        self.mbox = mailbox.mbox('agent'+str(idAgent))
        self.mbox.clear()
    
        self.thread_pI = threading.Thread(target=self.thread_processImage) #,daemon=True)
        self.thread_rL = threading.Thread(target=self.thread_recLoop) #,daemon=True)
        
        threading.Timer(1,self.thread_processImage)
        threading.Timer(1,self.thread_recLoop)
        
        
        self.clear()
    
    def run(self):
        self.thread_pI.start()
        self.thread_rL.start()
         
        #self.thread_pI.join()
        #self.thread_rL.join()
    
    def writeLog(self, message):
        return 'agent '+str(self.id)+' '+message

    def thread_processImage(self):
        t = 0
        while(True):
            time.sleep(0.2)
            
            self.defineWhomToSend(t)
            t = t + 1
        
     
    def thread_recLoop(self):
        t = 0
        while(True):
            time.sleep(0.2)
            self.recMess()
            t = t + 1
    
    def defineWhomToSend(self,m):
        if(self.id == TARGET1):
                self.sendMess("Hello "+str(m),TARGET0)
        elif(self.id == TARGET0 ):
                self.sendMess("Hello "+str(m),TARGET1)
        
    def parseRecMess(self,m):
        print(m)
        return 0
        
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
                if(is_ACK_NACK == 1):
                    message = "Ack ..."
                    #succes = self.sendMess(self, message, sender_ID)
                elif(is_ACK_NACK == 2):
                    succes = message = "Nack ..."
                    #self.sendMess(self, message, sender_ID)
                                        
        except mailbox.ExternalClashError:
            print("not possible to read the message")
        except FileExistsError:
            print("file does not exist ??")
    
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
            #message not sent
            print("not possible to send the message")
        except FileExistsError:
            print("file does not exist ??")
        return succes
    
    def clear(self):
        #if(self.thread_pI.is_alive() == False and self.thread_pI.is_alive() == False):
        self.mbox.close()
  
        
if __name__ == "__main__":
    
    agent0 = Agent(TARGET0)
    agent1 = Agent(TARGET1)
    agent0.run()
    agent1.run()
    
    cdt1 = agent0.thread_pI.is_alive() #or agent0.thread_rL.is_alive()
    cdt2 = agent1.thread_pI.is_alive() #or agent1.thread_rL.is_alive()
    
    t = 0
    while(t < 100):
        t = t+1
        time.sleep(2)
    exit(0)
    
    
    