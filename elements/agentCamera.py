import threading
import mailbox
import time
import logging
import numpy as np
from elements.agent import *
from elements.target import *
from utils.infoAgentCamera import *
from utils.message import *

NAME_MAILBOX = "mailbox/MailBox_Agent"


class AgentCam(Agent):
    def __init__(self, idAgent, camera, room):
        # Attributes
        self.cam = camera
        self.cam.camDesactivate()
        self.memory = InformationMemory(20)

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

    def thread_processImage(self):
        state = "takePicture"
        nextstate = state

        my_time = self.myRoom.time
        my_previousTime = my_time - 1

        picture = []
        while (self.threadRun == 1):

            state = nextstate
            my_time = self.myRoom.time

            if my_time > -1:
                self.cam.camActivate()

            if state == "takePicture":
                picture = self.cam.takePicture(self.myRoom.targets)
                # if the room dispositon has evolved we create a new
                if (not self.cam.isActivate()):
                    time.sleep(0.2)
                    nextstate = "takePicture"

                elif (my_previousTime != my_time):
                    my_previousTime = my_time
                    self.updateMemory("newPicture", picture)
                    s = self.memory.memoryToString()
                    self.log_room.info(s)
                    nextstate = "makePrediction"  # Avoir si on peut améliorer les prédictions avec les mess recu
                else:
                    nextstate = "processData"


            elif state == "makePrediction":
                # Prediction based on a picture
                prediction = self.cam.predictPaths()
                nextstate = "processData"

            elif nextstate == "processData":
                # Prediction based on messages
                # All the message a written based on the value of my_time
                self.processInfoMemory(my_time)
                nextstate = "sendMessage"

            elif state == "sendMessage":
                cdt1 = self.info_messageSent.getSize() > 0
                cdt2 = self.info_messageReceived.getSize() > 0
                cdt3 = self.info_messageToSend.getSize() > 0

                if cdt1 or cdt2 or cdt3:
                    pass
                    # self.log_room.info(self.info_messageSent.printMyList())
                    # self.log_room.info(self.info_messageReceived.printMyList())
                    # self.log_room.info(self.info_messageToSend.printMyList())

                self.info_messageSent.removeMessageAfterGivenTime(my_time, 10)
                self.info_messageReceived.removeMessageAfterGivenTime(my_time, 10)
                self.sendAllMessage()

                if MULTI_THREAD != 1:
                    self.recAllMess()
                    self.processRecMess()
                else:
                    time.sleep(0.2)

                nextstate = "takePicture"

            else:
                print("FSM not working proerly")

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

                typeMessage = "ack"
                if self.memory.isTargetDetected(self.myRoom.time, rec_mes.targetRef):
                    # If the target is seen => distances # AJouté la condition
                    # if(distance < distance 2)
                    # typeMessage="ack"
                    # else:
                    typeMessage = "nack"

                    # Update Info
                self.updateMemory("infoFromOtherCam", rec_mes)
                # Response
                self.sendMessageType(typeMessage, rec_mes, False)


            elif (rec_mes.messageType == "locked"):
                # Update Info
                self.updateMemory("infoFromOtherCam", rec_mes)
                # Response
                self.sendMessageType("ack", rec_mes, False)


            elif (rec_mes.messageType == "ack" or rec_mes.messageType == "nack"):
                for sent_mes in self.info_messageSent.getList():
                    added = sent_mes.add_ACK_NACK(rec_mes)
                    if added:
                        if sent_mes.messageType == "request":
                            if sent_mes.is_approved():
                                # Update Info
                                self.updateMemory("infoFromOtherCam", sent_mes)
                                # Response
                                self.sendMessageType("locked", sent_mes, True)

                            elif sent_mes.is_not_approved():
                                pass  # do some stuff


            elif (rec_mes.messageType == "heartbeat"):
                pass

            else:
                pass

            # message supress from the wainting list
            self.info_messageReceived.delMessage(rec_mes)


if __name__ == "__main__":
    pass
