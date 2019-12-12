import numpy as np
import random
import re


class Message():
    def __init__(self,timeStamp,senderID,senderSignature,messageType,message,targetID=-1):
        self.timeStamp = timeStamp
        self.signature = int(random.random() * 10000000000000000)
        
        self.senderID = int(senderID)
        self.senderSignature = int(senderSignature)
        self.receiverID_Signature = []
        self.remainingReceiver = []

        self.targetRef = targetID
        
        self.message = message
        self.messageType = messageType

    def getReceiverNumber(self):
        return len(self.receiverID_Signature)

    def addReceiver(self, receiverID, receiverSignature):
        if int(receiverSignature) >= 100:
            self.receiverID_Signature.append([int(receiverID), int(receiverSignature)])
            self.remainingReceiver.append([receiverID, receiverSignature])

    def clearReceiver(self):
        self.receiverID_Signature = []
        self.remainingReceiver = []

    def notifySendTo(self, receiverID, receiverSignature):
        for message in self.remainingReceiver:
            if message[0] == receiverID and message[1] == receiverSignature:
                self.remainingReceiver.remove(message)

    def isMessageSentToEveryReceiver(self):
        if len(self.remainingReceiver) == 0:
            return True
        else:
            return False

    def modifyMessageFromString(self,s):
        self.clearReceiver()
        s = s.replace("\n","")
        s = s.replace(" ","")
        attribut = re.split("Timestamp:|message#:|From:|sender#|Receiverlist:|Type:|target:|Message:",s)
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
        self.targetRef = attribut[7]
        self.message = attribut[8]
        
    def formatMessageType(self):
        s1 = "Timestamp: "+str(self.timeStamp)+' message#:'+str(self.signature)+"\n"
        s2 = "From: " + str(self.senderID)+" sender#" +str(self.senderSignature)+"\nReceiver list : \n"
        s3 = ""
        for receiver in self.receiverID_Signature:
            s3 = s3 + "To: "+ str(receiver[0]) +" receiver#"+str(receiver[1])+"\n"
            
        s4 = 'Type: '+str(self.messageType) + " target: "+str(self.targetRef)+  " Message: "
        base = s1+s2+s3+s4
        return base + str(self.message) +"\n"
class Message_Check_ACK_NACK(Message):
    def __init__(self, timeStamp, senderID, senderSignature, messageType, message, targetID=-1):
        self.ack = []
        self.nack = []
        super().__init__(timeStamp, senderID, senderSignature, messageType, message, targetID)

    def get_AckNumber(self):
        return len(self.ack)

    def get_NackNumber(self):
        return len(self.nack)

    def is_not_approved(self):
        if self.messageType == 'request':
            if self.get_NackNumber() > 0:
                return True
            else:
                return False

    def is_approved(self):
        if self.messageType == 'request':
            if int(self.get_AckNumber()) >= int(self.getReceiverNumber()):
                return True
            else:
                return False

    def add_ACK_NACK(self, rec_message):
        if rec_message.messageType == 'ack' or rec_message.messageType == 'nack':
            if (self.signature == int(rec_message.message)):
                if (rec_message.messageType == "ack"):
                    self.ack.append(rec_message)
                elif (rec_message.messageType == "nack"):
                    self.nack.append(rec_message)
            return True
        else:
            return False

    def getMessageInACK_NACK(self):
        if (self.messageType == "ack" or self.messageType == "nack"):
            message_in = Message(0, 0, 0, 0, 0)
            message_in.modifyMessageFromString(self.formatMessageType())
        else:
            message_in = None
        return message_in

''' List of messages '''
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
            if message.timeStamp + deltaTime <= time:
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
    
    def isMessageWithSameTypeSameAgentRef(self,messageToFind):
        for message in self.myList:
            if message.targetRef == messageToFind.targetRef and message.messageType == messageToFind.messageType :
                return True
        return False
                
    
    def printMyList(self):
        s = self.name + "\n"
        for message in self.myList:
            s = s + message.formatMessageType()+"\n" 
        return s
                

        
        
        
            
            
        