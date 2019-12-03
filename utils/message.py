import numpy as np
import random

class Message():
    def __init__(self,timeStamp,senderID,senderSignature,receiverID,receiverSignature, messageType,message):
        self.senderID = senderID
        self.senderSignature = senderSignature
        self.receiverID = receiverID
        self.receiverSignature = receiverSignature
        self.message = message
        self.messageType = messageType
        self.timeStamp = timeStamp
        self.signature = random.random() * 10000000000000000
        self.formatMessageType()

    def modifyMessageFromString(self,s):
        att = s.split("-")
        self.senderID = att[2]
        self.senderSignature = [3]
        self.receiverID = att[4]
        self.receiverSignature = [5]
        self.message = att[7]
        self.messageType = att[6]
        self.timeStamp = att[1]
        self.signature = float(att[0])
        self.formatMessageType()
        
    def formatMessageType(self):
        base =  str(self.signature)+'-'+ str(self.timeStamp)+'-'+str(self.senderID)+'-'+str(self.senderSignature)+'-'+str(self.receiverID)+'-'+str(self.receiverSignature)+'-'+str(self.messageType)
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
        s1 = 'message #'+str(self.signature)+' - time :'
        s2 = str(self.timeStamp) + '- from agent :'+str(self.senderID)+' - to agent :'+str(self.receiverID)
        s3 = ' - '+self.messageType + ' - '+str(self.message)
        return  s1+s2+s3
    
        
        
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