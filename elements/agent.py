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

        self.mbox = mailbox.mbox(NAME_MAILBOX + str(self.id))
        self.mbox.clear()

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

        # Startrun()
        self.log_message.info('Agent initialized and  starts')


    ############################
    #   Receive Information
    ############################
    def parseRecMess(self, m):
        # reconstruction de l'objet message
        rec_mes = Message(0, 0, 0, 0, 0)
        rec_mes.modifyMessageFromString(m)

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
                    self.log_message.info('SEND     : \n' + m.formatMessageType())
                    mbox.flush()
                    m.notifySendTo(receiver[0], receiver[1])

                    if m.isMessageSentToEveryReceiver():
                        succes = 0
                    else:
                        succes = 1  # message partially sent
                finally:
                    mbox.unlock()

            ##############################
                if MULTI_THREAD != 1:
                    pass
                    # Agentreceive.recAllMess()
                    # Agentreceive.processRecMess()
            ##############################
            except mailbox.ExternalClashError:
                self.log_message.debug("Not possible to send messages")
            except FileExistsError:
                self.log_message.warning("Mailbox file error SEND")

        return succes

    ############################
    # Other
    ############################

    def clear(self):
        self.threadRun = 0
        while (self.thread_pI.is_alive() and self.thread_pI.is_alive()):
            pass
        self.mbox.close()


if __name__ == "__main__":
    pass
