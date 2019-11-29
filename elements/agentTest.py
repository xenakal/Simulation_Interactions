Class AgentTest: 

    def __init__(self, idAgent):
        thread1 = new Thread(recLoop)
        thread2 = new Thread(processImages)
        self.id = idAgent
        self.otherCamInfo = new np.array([])

    def processImage(self):
        cam = Camera(idAgent, ...)
        while Alive: 
            cam.run()

    def recLoop(self): 
        while Alive: 
            while buff not empty: 
                recMess(...)
                storeInfo(m)

    def recMess(self, m, senderID):
        if (m=="Request target 1"):
            d = ...
            #check if we see target 1
            if (!view(target1)):
                sendMess(idSender, "ACK")
            else: 
                if(d < distanceToTarget1):
                    sendMess(idSender, "ACK")
                else:
                    sendMess(idSender, "NACK")

        elif (m=="ACK"):
            self.acksReceived[m.info].append(senderID)

        elif (m=="NACK"):
            self.master = False



    def sendMess(cID, message):
        cID.mailboxAdd(message, priority, ...)

    def storeInfo(self,m):
        # put relvant part of m in self.otherCamInfo

