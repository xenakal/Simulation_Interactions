import numpy as np
import random
import re


class Message():
    def __init__(self,timeStamp,senderID,senderSignature,messageType,message):
        self.senderID = int(senderID)
        self.senderSignature = int(senderSignature)
        self.receiverID_Signature = []
        self.message = message
        self.messageType = messageType
        self.timeStamp = timeStamp
        self.signature = int(random.random() * 10000000000000000)
        
        self.remainingReceiver = []

    def modifyMessageFromString(self,s):
        
        self.clearReceiver()
        
        s = s.replace("\n","")
        s = s.replace(" ","")
        attribut = re.split("Timestamp:|message#:|From:|sender#|Receiverlist:|Type:|Message:",s)
        
        
        self.timeStamp = int(attribut[1])
        self.signature = int(attribut[2])
        self.senderID = int(attribut[3])
        self.senderSignature = int(attribut[4])
        
        receivers = re.split("To:",attribut[5])
        for receiver in receivers:
            info = receiver.split("receiver#")
            try:
                if(info == ""):
                    pass #end of the chain
                else:
                    self.addReceiver(info[0],info[1])
                    pass
            except IndexError:
                pass
            
        self.messageType = attribut[6]   
        self.message = attribut[7]
        
    def formatMessageType(self):
        s1 = "Timestamp: "+str(self.timeStamp)+' message#:'+str(self.signature)+"\n"
        s2 = "From: " + str(self.senderID)+" sender#" +str(self.senderSignature)+"\nReceiver list : \n"
        s3 = ""
        for receiver in self.receiverID_Signature:
            s3 = s3 + "To: "+ str(receiver[0]) +" receiver#"+str(receiver[1])+"\n"
            
        s4 = 'Type: '+str(self.messageType) + " Message: "
        base = s1+s2+s3+s4
            
        return base + str(self.message) +"\n"
    
    def parseMessageType(self):    
        return self.message
        
    def printMessage(self):
        print(self.formatMessageType())
        
    def getMessageInACK_NACK(self):
        if (self.messageType == "ack" or self.messageType == "nack"):
            message = Message(0,0,0,0,0,0)
            message.modifyMessageFromString(self.formatMessageType)
        else:
            message = -1
        return message
    
    def getReceiverNumber(self):
        return len(self.receiverID_Signature)
    
    def addReceiver(self,receiverID,receiverSignature):
        if int(receiverSignature) >=100 :
            self.receiverID_Signature.append([int(receiverID),int(receiverSignature)])
            self.remainingReceiver.append([receiverID,receiverSignature])
    
    def clearReceiver(self):
        self.receiverID_Signature = []
        self.remainingReceiver = [] 
        
    def notifySendTo(self,receiverID,receiverSignature):
        for message in self.remainingReceiver:
            if message[0] == receiverID and message[1] == receiverSignature:
                self.remainingReceiver.remove(message)
    
    def isMessageSentToEveryReceiver(self):
        if len(self.remainingReceiver)==0:
            return True
        else:
            return False
        
class ListMessage():
    def __init__(self,name):
        self.myList = []
        self.name = name
    
    def getSize(self):
        return len(self.myList)
    
    def getList(self):
        return self.myList.copy()
    
    def addMessage(self,message):
        self.myList.append(message)
        
    def delMessage(self,message):
        self.myList.remove(message)
    
    def removeMessageAfterGivenTime(self,time,deltaTime):
        for message in self.myList:
            if message.timeStamp + deltaTime >= time:
                self.myList.remove(message)
    
    def receiverInCommun_WithSimilarMessage_InList(self,messageToFind):
        receiverInCommun = []
        for message in self.myList:
            if message.messageType == messageToFind.messageType and message.message == messageToFind.message:
                for receiver in message.receiverID_Signature:
                    ID = receiver[0]
                    Signature = receiver[1]
                    for receiverCompare in messageToFind.receiverID_Signature:
                        IDCompare = receiverCompare[0]
                        SignatureCompare = receiverCompare[1]
                        if ID == IDCompare and Signature == SignatureCompare:
                            receiverInCommun.append(receiver)
                            break
                        
        return receiverInCommun.copy()
    
    def receiverMissing_WithSimilarMessage_InList(self,messageToFind):
        receiverInCommun = self.receiverInCommun_WithSimilarMessage_InList(messageToFind)
        receiverMissing = []
               
        if len(receiverInCommun) >= len(messageToFind.receiverID_Signature):
            return receiverMissing
        
        else:
            receiverMissing = messageToFind.receiverID_Signature.copy()
            for receiver in messageToFind.receiverID_Signature:
                ID = receiver[0]
                Signature = receiver[1]
                for receiverCompare in receiverInCommun:
                    IDCompare = receiverCompare[0]
                    SignatureCompare = receiverCompare[1]                           
                    if ID == IDCompare and Signature == SignatureCompare:
                        receiverMissing.remove(receiver)
                        break
            return receiverMissing
                                    
    
    def isMessageInTheList(self,messageToFind):
        for message in self.myList:
            if message.signature == messageToFind.signature:
                return True
            
        return False
    
    def isMessageWithSameMessage(self,messageToFind):
        for message in self.myList:
            if message.message == messageToFind.message:
                return True
        return False
                
    
    def printMyList(self):
        s = self.name + "\n"
        for message in self.myList:
            s = s + message.formatMessageType()+"\n" 
        return s
    
class reponseHandler_Message():
    def __init__(self,message):
        self.message = message
        self.ack = []
        self.nack = []
        
    def get_ack(self):
            return self.ack.copy()
        
    def get_nack(self):
        return self.nack.copy()
    
    def get_AckNumber(self):
        return len(self.ack)
    
    def get_NackNumber(self):
        return len(self.nack)
    
    def is_numberACK_NACK_complete(self):
        if message.messageType == 'request' or message.messageType == 'aquire':
            if self.get_AckNumber + self.get_NackNumber  >= self.message.getReceiverNumber():
                return True
            else:
                return False
            
    def is_Approved(self):
        if message.messageType == 'request' or message.messageType == 'aquire':
            if self.get_AckNumber >= self.message.getReceiverNumber():
                return True
            else:
                return False
                
        
    def add(self,rec_message):
        if self.messageType == 'ack' or self.messageType == 'nack':
             if (self.message.signature == rec_message.getMessageInACK_NACK().signature):
                if(rec_message.messageType == "ack"):
                    self.ack.append(rec_message)        
                elif (rec_messsage.messageType == "nack"):
                    self.nack.append(rec_message)
                
if __name__ == "__main__":
        message1 = Message(0,1,545448,'request','salut')
        message1.addReceiver(0,10000)
        
        message2 = Message(0,1,545448,'ack','Hey salut')
        message2.addReceiver(0,10000)
        message2.addReceiver(1,10500)
        
        
        message3 = Message(0,1,545448,'request','salut')
        message3.addReceiver(0,10000)
        message3.addReceiver(1,10500)
        
        messageList = ListMessage("test")
        messageList.addMessage(message1)
        messageList.addMessage(message2)
        
        
        print(messageList.printMyList())
        print(messageList.isMessageInTheList(message2))
        print(messageList.isMessageInTheList(message3))
        print(messageList.isMessageWithSameMessage(message2))
        print(messageList.isMessageWithSameMessage(message3))
        print(messageList.receiverInCommun_WithSimilarMessage_InList(message3))
        print(messageList.receiverMissing_WithSimilarMessage_InList(message3))
        print(messageList.receiverInCommun_WithSimilarMessage_InList(message2))
        print(messageList.receiverMissing_WithSimilarMessage_InList(message2))
    
        
        
        
            
            
        