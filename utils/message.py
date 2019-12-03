import numpy as np
import random

class Message():
    def __init__(self,timeStamp,senderID, receiverID, messageType,message):
        self.senderID = senderID
        self.receiverID = receiverID
        self.message = message
        self.messageType = messageType
        self.timeStamp = timeStamp
        self.specialNumber = random.random() * 10000000000000000
        self.formatMessageType()

    def modifyMessageFromString(self,s):
        att = s.split("-")
        self.senderID = att[2]
        self.receiverID = att[3]
        self.message = att[5]
        self.messageType = att[4]
        self.timeStamp = att[1]
        self.specialNumber = float(att[0])
        self.formatMessageType()
        
    def formatMessageType(self):
        base =  str(self.specialNumber)+'-'+ str(self.timeStamp)+'-'+str(self.senderID)+'-'+str(self.receiverID)+'-'+str(self.messageType)
        if self.messageType == 'request' or self.messageType == 'request_all':
            message = "target" + '_' + str(self.message)
        elif self.messageType == 'ack' or self.messageType == 'nack':
            message = self.message
        elif self.messageType == 'information':
            message = self.message
        elif self.messageType == 'information':
            message = self.message
        else:
            message = ""
            
        return base +'-'+ message
    
    def parseMessageType(self):
        if self.messageType == 'request' or self.messageType == 'request_all':
            att = self.message.split('_')
            message = att[1]  #information utile 
        elif self.messageType == 'ack' or self.messageType == 'nack':
            message = self.message
        elif self.messageType == 'information':
            message = self.message
        elif self.messageType == 'information':
            message = self.message
        else:
            message = self.message
            
        return message
        
    def printMessage(self):
        return 'message #'+str(self.specialNumber)+' - time :' + str(self.timeStamp) + '- from agent :'+str(self.senderID)+' - to agent :'+str(self.receiverID)+' - '+self.messageType + ' - '+str(self.message)
        
        
class ListMessage():
    def __init__(self,name):
        self.myList = []
        self.name = name
        
    def getList(self):
        return self.myList.copy()
    
    def addMessage(self,message):
        self.myList.append(message)
        
    def delMessage(self,message):
        self.myList.remove(message)
    
    def findMessage(self,message):
        pass #à implémenter
    
    def printMyList(self):
        s = self.name + "\n"
        for message in self.myList:
            s = s + message.printMessage() +  "\n"
        
        return s