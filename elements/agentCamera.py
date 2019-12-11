import threading
import mailbox
import time
import logging
import numpy as np
from elements.agent import *
from elements.target import *
from utils.infoAgentCamera import *
from utils.message import *

TIME_PICTURE = 0.2
TIME_SEND_READ_MESSAGE = 0.05

MULTI_THREAD = 0
NAME_MAILBOX = "mailbox/MailBox_Agent"

class AgentCam(Agent):
    def __init__(self, idAgent, camera, room):
        # Attributes
        self.cam = camera
        #self.cam.camDesactivate()
        self.memory = InformationMemory(20)

        # Threads
        self.threadRun = 1
        self.thread_pI = threading.Thread(target=self.thread_processImage)
        self.thread_rL = threading.Thread(target=self.thread_recLoop)

        # log_room
        logger_room = logging.getLogger('room' + str(idAgent))
        logger_room.setLevel(logging.INFO)
        # create file handler which log_messages even debug messages
        fh = logging.FileHandler(NAME_LOG_PATH + str(idAgent) + "-room", "w+")
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log_message level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger_message
        logger_room.addHandler(fh)
        logger_room.addHandler(ch)

        self.log_room = logger_room

        super().__init__(idAgent, room)

    def run(self):
        self.thread_pI.start()
        if MULTI_THREAD == 1:
            self.thread_rL.start()

    def thread_processImage(self):
        state = "takePicture"
        nextstate = state
        my_previousTime = self.myRoom.time - 1

        while (self.threadRun == 1):
            state = nextstate

            if state == "takePicture":
                picture = self.cam.takePicture(self.myRoom.targets)
                time.sleep(TIME_PICTURE)

                # if the room dispositon has evolved we create a new
                if (not self.cam.isActivate()):
                    nextstate = "takePicture"
                else:
                    my_previousTime = self.myRoom.time
                    self.updateMemory("newPicture", picture)
                    self.log_room.info(self.memory.memoryToString())
                    nextstate = "processData"  # Avoir si on peut améliorer les prédictions avec les mess recu


            elif nextstate == "processData":
                # self.memory.makePredictions()
                # self.processInfoMemory(my_time)
                nextstate = "sendMessage"

            elif state == "sendMessage":
                self.info_messageSent.removeMessageAfterGivenTime(self.myRoom.time, 10)
                self.info_messageReceived.removeMessageAfterGivenTime(self.myRoom.time, 10)
                #self.sendAllMessage()
                if MULTI_THREAD != 1:
                    pass
                    #self.recAllMess()
                    #self.processRecMess()

                time.sleep(TIME_SEND_READ_MESSAGE)
                nextstate = "takePicture"
            else:
                print("FSM not working proerly")

    def thread_recLoop(self):
        while self.threadRun == 1:
                self.recAllMess()
                self.processRecMess()

    #################################
    #   Store and process information
    ################################# 
    def updateMemory(self, type_update, objet):
        # create a new colums in the table to save the information of the picture
        if type_update == "newPicture":
            # copy the information from last time, all the target unseen
            self.memory.addNewTime(self.myRoom.time)
            picture = objet
            # adding all the target seen
            for elem in picture:
                targetObj = elem[0]
                # When added from the previous time value
                # The target is by default unseen
                # If it is seen in the picture this line changes the value
                self.memory.addTarget(self.myRoom.time, targetObj)
                self.memory.setSeenByCam(self.myRoom.time, targetObj, True)  # set that the target is seen

        # modify the information of the message
        elif type_update == "infoFromOtherCam":
            message = objet
            if message.messageType == "request":
                if message.is_approved():  # if a request is succesfull
                    self.memory.setfollowedByCam(self.myRoom.time, message.targetRef, self.id)
                else:  # check to see if a target can be discover by the cam during a request
                    self.memory.addTargetFromID(self.myRoom.time, message.targetRef, self.myRoom)

            elif message.messageType == "locked":  # Ohter camera knos that the target is lock
                self.memory.setfollowedByCam(self.myRoom.time, message.targetRef, message.senderID)

            elif message.messageType == "ack" or message.messageType == "nack":
                pass

            elif message.messageType == "heartbeat":
                pass

        else:
            pass

    # define what message to send in terms of the info store in memory
    def processInfoMemory(self, time):
        # IMPORTANT we can decide on which time we base the message we send
        try:
            index = self.memory.computeIndexBasedOnTime(time)
            myList = self.memory.info_room[index]
        except IndexError:
            print("error1")
            myList = self.memory.info_room[len(self.memory.info_room) - 1]

        for info in myList:

            if info.target.label == "target":
                # if the cam sees the object and the object is not followed by an ohter cam
                if info.seenByCam and info.followedByCam == -1:
                    # Then send a request to follow this target
                    # Also signal to other cam that this target exit
                    dx = self.cam.xc - info.target.xc
                    dy = self.cam.yc - info.target.yc
                    distance = math.pow(dx * dx + dy * dy, 0.5)
                    self.sendMessageType('request', distance, True, info.target.id)

            elif info.target.label == "obstruction":
                pass
            elif info.target.label == "fix":
                pass

    def processRecMess(self):
        for rec_mes in self.info_messageReceived.getList():
            if (rec_mes.messageType == "request"):
                self.received_message_request(rec_mes)
            elif (rec_mes.messageType == "locked"):
                self.received_message_locked(rec_mes)
            elif (rec_mes.messageType == "ack" or rec_mes.messageType == "nack"):
                self.received_message_ackNack(rec_mes)

            self.info_messageReceived.delMessage(rec_mes)

    def send_message_request(self,information,target,receiverList,to_all):
        m = Message(self.myRoom.time, self.id, self.signature, "request", information, target)
        if to_all:
            for agent in self.myRoom.agentCam:
                if (agent.id != self.id):
                    m.addReceiver(agent.id, agent.signature)
        cdt1 = m.getReceiverNumber() > 0
        cdt2 = self.info_messageToSend.isMessageWithSameTypeSameAgentRef(m)
        cdt3 = self.info_messageSent.isMessageWithSameTypeSameAgentRef(m)
        if cdt1 and not cdt2 and not cdt3:
            self.info_messageToSend.addMessage(m)

    def send_message_locked(self,message,to_all):
        m_format = Message(self.myRoom.time, self.id, self.signature, "locked", message.signature, message.targetRef)
        if to_all:
            for agent in self.myRoom.agentCam:
                if (agent.id != self.id):
                    message.addReceiver(agent.id, agent.signature)
        self.info_messageToSend.addMessage(message)

    def send_message_ackNack(self,message,typeMessage):
        m = Message(self.myRoom.time, self.id, self.signature, typeMessage, message.signature, message.targetRef)
        m.addReceiver(message.senderID, message.senderSignature)
        self.info_messageToSend.addMessage(m)

    def received_message_request(self,message):
        typeMessage = "ack"
        if self.memory.isTargetDetected(self.myRoom.time, message.targetRef):
            # If the target is seen => distances # AJouté la condition
            # if(distance < distance 2)
            # typeMessage="ack"
            # else:
            typeMessage = "nack"

        # Update Info
        self.updateMemory("infoFromOtherCam",message)
        # Response
        self.send_message_ackNack(self,message,typeMessage)

    def received_message_locked(self,message):
        # Update Info
        self.updateMemory("infoFromOtherCam", message)
        # Response
        self.send_message_ackNack(self, message,"ack")

    def received_message_ackNack(self,message):
        for sent_mes in self.info_messageSent.getList():
            added = sent_mes.add_ACK_NACK(message)
            if added:
                if sent_mes.messageType == "request":
                    if sent_mes.is_approved():
                        # Update Info
                        self.updateMemory("infoFromOtherCam", sent_mes)
                        # Response
                        self.send_message_locked()
                    elif sent_mes.is_not_approved():
                        pass  # can be directly remove



if __name__ == "__main__":
    pass
