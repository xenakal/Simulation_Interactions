import threading
import mailbox
import time


class AgentCam:
    def __init__(self, idAgent,camera,room):
        self.id = idAgent
        self.cam = camera
        self.myRoom = room
        self.mbox = mailbox.mbox('agent'+str(idAgent))
        self.mbox.clear()
    
        self.thread_pI = threading.Thread(target=self.thread_processImage,args=(self.myRoom,)) #,daemon=True)
        self.thread_rL = threading.Thread(target=self.thread_recLoop) #,daemon=True)
        
        threading.Timer(1,self.thread_processImage)
        threading.Timer(1,self.thread_recLoop)
        
        self.run()
        #self.clear()
    
    def run(self):
        pass
        self.thread_pI.start()
        self.thread_rL.start()
         
        #self.thread_pI.join()
        #self.thread_rL.join()

    def thread_processImage(self,myRoom):
        while(True):
            self.cam.run(myRoom)
            self.defineWhomToSend("Hello ",myRoom)
            time.sleep(0.2) 
            
    def thread_recLoop(self):
        while(True):
            time.sleep(0.2)
            self.recMess()
            
    
    def defineWhomToSend(self,m,myRoom):
        #pour le moemnt les camera s'envoie des hello 
        for agent in myRoom.agentCam:
            if(agent.id != self.id):
                self.sendMess(m +str(agent.id),agent.id)
        
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
                if(is_ACK_NACK == 1):
                    message = "Ack ..."
                    succes = self.sendMess(self, message, sender_ID)
                elif(is_ACK_NACK == 2):
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
    
    #J'ai pas encore trouvé comment faire ça de manière propre
    def clear(self):
        #if(self.thread_pI.is_alive() == False and self.thread_pI.is_alive() == False):
        self.mbox.close()
  
        
if __name__ == "__main__":
    pass
 
    
    
    
