import threading
import mailbox
import time
import logging
import numpy as np
from elements.target import *
from utils.message import *

NAME_LOG_PATH = "log/log_agent/Agent"
NAME_MAILBOX = "mailbox/MailBox_Agent"

class Agent:
    def __init__(self, idAgent, room):
        # Attributes
        self.id = idAgent
        self.myRoom = room
        self.signature = int(random.random() * 10000000000000000) + 100  # always higher than 100

        # Communication
        self.info_messageSent = ListMessage("Sent")
        self.info_messageReceived = ListMessage("Received")
        self.info_messageToSend = ListMessage("ToSend")
        self.message_stat = Agent_statistic(idAgent)

        mbox = mailbox.mbox(NAME_MAILBOX + str(self.id))
        mbox.clear()

        # Threads
        self.threadRun = 1
        self.thread_pI = threading.Thread(target=self.thread_processImage)
        self.thread_rL = threading.Thread(target=self.thread_recLoop)
        # log_message
        threading.Timer(2,self.thread_processImage)
        threading.Timer(2,self.thread_recLoop)

        # create logger_message with 'spam_application'
        logger_message = logging.getLogger('agent' + str(self.id))
        logger_message.setLevel(logging.INFO)
        # create file handler which log_messages even debug messages
        fh = logging.FileHandler(NAME_LOG_PATH + str(self.id) + "-messages", "w+")
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

    ############################
    #   Receive Information
    ############################
    def parseRecMess(self, m):
        # reconstruction de l'objet message
        rec_mes = Message(0, 0, 0, 0, 0)
        rec_mes.modifyMessageFromString(m)

        self.message_stat.count_message_received(rec_mes.senderID)
        self.info_messageReceived.addMessage(rec_mes)
        self.log_message.info('RECEIVED : \n' + rec_mes.formatMessageType())

    def recAllMess(self):
        succes = -1
        # Reading the message
        mbox_rec = mailbox.mbox(NAME_MAILBOX + str(self.id))
        try:
            mbox_rec.lock()
            keys = mbox_rec.keys()
            try:
                succes = 0
                for key in keys:
                    m = mbox_rec.get_string(key)

                    if m != "":
                        self.parseRecMess(m)  # We put the message in the stack of received message BUT not response !

                        if succes == 0:  # if we respond then the message is remove from the mail box
                            mbox_rec.remove(key)
                            mbox_rec.flush()
            finally:
                mbox_rec.unlock()

        except mailbox.ExternalClashError:
            self.log_message.debug("Not possible to read messages")
        except FileExistsError:
            self.log_message.warning("Mailbox file error RECEIVE")
        except PermissionError:
            self.log_message.warning("Windows error")

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

    # la fonction renvoie -1 quand le message n'a pas été envoyé mais ne s'occupe pas de le réenvoyer !
    def sendMess(self, m):
        succes = -1
        for receiver in m.remainingReceiver:
            try:
                mbox = mailbox.mbox(NAME_MAILBOX + str(receiver[0]))
                mbox.lock()
                try:
                    mbox.add(m.formatMessageType())  # apparament on ne peut pas transférer d'objet
                    self.message_stat.count_message_send(receiver[0])

                    mbox.flush()
                    m.notifySendTo(receiver[0], receiver[1])
                    if m.isMessageSentToEveryReceiver():
                        self.log_message.info('SEND     : \n' + m.formatMessageType())
                        succes = 0
                    else:
                        succes = 1  # message partially sent
                finally:
                    mbox.unlock()

            except mailbox.ExternalClashError:
                self.log_message.debug("Not possible to send messages")
            except FileExistsError:
                self.log_message.warning("Mailbox file error SEND")
            except PermissionError:
                self.log_message.warning("Windows error")
            except FileNotFoundError:
                self.log_message.warning("Mailbox file error SEND")

        return succes

    ############################
    # Other
    ############################

    def clear(self):
        self.threadRun = 0
        while (self.thread_pI.is_alive() and self.thread_pI.is_alive()):
            pass
        mbox = mailbox.mbox(NAME_MAILBOX + str(self.id))
        mbox.close()

class Agent_statistic:
    def __init__(self,id):
        self.id = id
        self.send_message_statistic = []
        self.receive_message_statistic = []

    def init_message_static(self,room):
        tab0 = []
        tab1 = []
        for camera in room.cameras:
            tab0.append([camera.id,0])
            tab1.append([camera.id,0])

        self.send_message_statistic = tab0.copy()
        self.receive_message_statistic = tab1.copy()

    def count_message_send(self,receiverID):
        for element in self.send_message_statistic:
                if element[0] == receiverID:
                    element[1] = element[1]+1

    def count_message_received(self,senderID):
        for element in self.receive_message_statistic:
                if element[0] == senderID:
                    element[1] = element[1]+1

    def to_string(self):
        s = "Statistic message \n"
        for element in self.send_message_statistic:
            if element[0] != self.id:
                s = s + "Sender agent: " + str(self.id) + " receiver agent: "+str(element[0]) + ", # messages = " + str(element[1]) +"\n"
        for element in self.receive_message_statistic:
            if element[0] != self.id:
                s = s + "Receiver agent: "+ str(self.id) + " sender agent: " + str(element[0])  + ", # messages = " + str(element[1]) +"\n"
        return s

if __name__ == "__main__":
    pass
