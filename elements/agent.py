import threading
import queue
import mailbox
import time

#pas utilisé autre solution
class Pipeline(queue.Queue):
    def __init__(self):
         super().__init__(maxsize=10)
 
    def get_message(self, name):
        logging.debug("%s:about to get from queue", name)
        value = self.get()
        logging.debug("%s:got %d from queue", name, value)
        return value
 
    def set_message(self, value, name):
        logging.debug("%s:about to add %d to queue", name, value)
        self.put(value)
        logging.debug("%s:added %d to queue", name, value)

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
        while(t < 5):
            #print("1 Agent"+str(self.id))
            time.sleep(1)
            self.defineWhomToSend(t)
            t = t + 1
        
        exit(0)
     
    def thread_recLoop(self):
        t = 0
        while(t < 5):
            #print("2 Agent"+str(self.id))
            time.sleep(1)
            self.recMess()
            t = t + 1
        
        exit(0)
    
    def defineWhomToSend(self,m):
        if(self.id == 8):
                self.sendMess("Hello "+str(m),9)
        elif(self.id == 9):
                self.sendMess("Hello "+str(m),8)
        
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
        return succes
    
    def clear(self):
        self.mbox.close()
  
        
if __name__ == "__main__":
    
    agent0 = Agent(8)
    agent1 = Agent(9)
    agent0.run()
    agent1.run()

    #agent0.clear()
    #agent1.clear()
    #exit(0)
    
    
#    def thread_agent0():
#        agent0 = Agent(0)
#        while(True):
#            agent0.sendMess("test",1)
#        #agent0.run()
#                
#    def thread_agent1():
#        agent1 = Agent(1)
#        #agent1.run()
#           
#    thread_0 = threading.Thread(target=thread_agent0,daemon=True)
#    thread_1 = threading.Thread(target=thread_agent1,daemon=True)
#    
#    thread_1.start()
#    thread_0.start()
#    
#    
#    thread_0.join()
#    thread_1.join()
                   
    
    
    