import threading
import mailbox
import time
import logging
import numpy as np
from elements.target import *
from multi_agent.agent import *
from multi_agent.estimator import *
from multi_agent.message import *
from multi_agent.memory import *
from multi_agent.linearPrediction import *

TIME_PICTURE = 0.05
TIME_SEND_READ_MESSAGE = 0.1

MULTI_THREAD = 0
NAME_MAILBOX = "mailbox/MailBox_Agent"


class AgentCam(Agent):

    def __init__(self, idAgent, camera, room):
        # Attributes
        self.cam = camera
        self.memory = Memory(idAgent)

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
        """
        One of the two main threads of an agent.
        """
        state = "takePicture"
        nextstate = state
        my_previousTime = self.myRoom.time - 1

        self.message_stat.init_message_static(self.myRoom)
        self.memory.init_memory(self.myRoom)

        while self.threadRun == 1:
            state = nextstate

            if state == "takePicture":
                picture = self.cam.takePicture(self.myRoom.targets)
                time.sleep(TIME_PICTURE)

                if not self.cam.isActivate():
                    nextstate = "takePicture"
                    time.sleep(0.3)
                else:
                    if my_previousTime != self.myRoom.time:  # Si la photo est nouvelle
                        my_previousTime = self.myRoom.time

                        for targetElem in picture:
                            self.memory.set_current_time(self.myRoom.time)
                            self.memory.add_create_target_estimator(self.myRoom, self.myRoom.time, targetElem[0].id,
                                                                    self.id, True)

                        self.log_room.info(self.memory.statistic_to_string() + self.message_stat.to_string())
                    nextstate = "processData"  # A voir si on peut améliorer les prédictions avec les mess recu

            elif nextstate == "processData":
                self.memory.makePredictions()
                self.process_InfoMemory(self.myRoom)
                self.memory.combine_data(self.myRoom)
                nextstate = "sendMessage"

            elif state == "sendMessage":
                self.info_messageSent.removeMessageAfterGivenTime(self.myRoom.time, 30)
                self.info_messageReceived.removeMessageAfterGivenTime(self.myRoom.time, 30)
                self.sendAllMessage()
                if MULTI_THREAD != 1:
                    pass
                    self.recAllMess()
                    self.process_Message_received()
                    self.process_Message_sent()

                time.sleep(TIME_SEND_READ_MESSAGE)
                nextstate = "takePicture"
            else:
                print("FSM not working proerly")

    def thread_recLoop(self):
        while self.threadRun == 1:
            self.recAllMess()
            self.process_Message_received()
            self.process_Message_sent()

    def process_InfoMemory(self, room):
        for target in room.targets:
            liste = self.memory.memory_agent.get_target_list(target.id)
            if len(liste) > 0:
                self.send_message_memory(liste[len(liste) - 1])

        for info in []:
            if info.target_label == "target":
                if info.seenByCam and info.followedByCam == -1:
                    dx = self.cam.xc - info.position[0]
                    dy = self.cam.yc - info.position[1]
                    distance = math.pow(dx * dx + dy * dy, 0.5)
                    self.send_message_request(distance, info.target_ID)

            elif info.target_label == "obstruction":
                pass
            elif info.target_label == "fix":
                pass

    def process_Message_sent(self):
        for message_sent in self.info_messageSent.getList():
            if message_sent.is_approved():
                if message_sent.messageType == "request":
                    # self.memory.setfollowedByCam(self.myRoom.time, message_sent.targetRef, self.id)
                    self.send_message_locked(message_sent)

                self.info_messageSent.delMessage(message_sent)
            elif message_sent.is_not_approved():
                self.info_messageSent.delMessage(message_sent)

    def process_Message_received(self):
        for rec_mes in self.info_messageReceived.getList():
            if rec_mes.messageType == "request":
                self.received_message_request(rec_mes)
            elif rec_mes.messageType == "memory":
                self.received_message_memory(rec_mes)
            elif rec_mes.messageType == "locked":
                self.received_message_locked(rec_mes)
            elif rec_mes.messageType == "ack" or rec_mes.messageType == "nack":
                self.received_message_ackNack(rec_mes)

            self.info_messageReceived.delMessage(rec_mes)

    def send_message_request(self, information, target, receivers=None):
        if receivers is None:
            receivers = []
        m = Message_Check_ACK_NACK(self.myRoom.time, self.id, self.signature, "request", information, target)
        if len(receivers) == 0:
            for agent in self.myRoom.agentCam:
                if agent.id != self.id:
                    m.addReceiver(agent.id, agent.signature)
        else:
            for receiver in receivers:
                m.addReceiver(receiver[0], receiver[1])

        cdt1 = self.info_messageToSend.isMessageWithSameTypeSameAgentRef(m)
        cdt2 = self.info_messageSent.isMessageWithSameTypeSameAgentRef(m)
        if not cdt1 and not cdt2:
            self.info_messageToSend.addMessage(m)

    def send_message_memory(self, memory, receivers=None):
        if receivers is None:
            receivers = []
        s = memory.to_string()
        s = s.replace("\n", "")
        s = s.replace(" ", "")

        m = Message_Check_ACK_NACK(self.myRoom.time, self.id, self.signature, "memory", s, memory.target_ID)
        if len(receivers) == 0:
            for agent in self.myRoom.agentCams:
                if agent.id != self.id:
                    m.addReceiver(agent.id, agent.signature)
        else:
            for receiver in receivers:
                m.addReceiver(receiver[0], receiver[1])

        cdt1 = self.info_messageToSend.isMessageWithSameMessage(m)
        if not cdt1:
            self.info_messageToSend.addMessage(m)

    def send_message_locked(self, message, receivers=None):
        if receivers is None:
            receivers = []
        m = Message_Check_ACK_NACK(self.myRoom.time, self.id, self.signature, "locked", message.signature,
                                   message.targetRef)
        if len(receivers) == 0:
            for agent in self.myRoom.agentCam:
                if agent.id != self.id:
                    m.addReceiver(agent.id, agent.signature)
        else:
            for receiver in receivers:
                m.addReceiver(receiver[0], receiver[1])

        self.info_messageToSend.addMessage(m)

    def send_message_ackNack(self, message, typeMessage):
        m = Message_Check_ACK_NACK(self.myRoom.time, self.id, self.signature, typeMessage, message.signature,
                                   message.targetRef)
        m.addReceiver(message.senderID, message.senderSignature)
        self.info_messageToSend.addMessage(m)

    def received_message_request(self, message):
        typeMessage = "ack"
        '''
        if self.memory.isTargetDetected(self.myRoom.time, message.targetRef):
            # If the target is seen => distances # AJouté la condition
            # if(distance < distance 2)
            # typeMessage="ack"
            # else:
            typeMessage = "nack"
        '''

        # Update Info
        # self.memory.addTargetEstimatorFromID(self.myRoom.time,self.id, message.targetRef, self.myRoom)
        # Response
        self.send_message_ackNack(message, typeMessage)

    def received_message_memory(self, message):
        # Update Info
        s = message.message
        if not (s == ""):
            target = Target()
            estimator = TargetEstimator(0, 0, target, 0, 0)

            estimator.parse_string(s)
            self.memory.add_target_estimator(estimator)
            # Response
            self.send_message_ackNack(message, "ack")

    def received_message_locked(self, message):
        # Update Info
        # self.memory.setfollowedByCam(self.myRoom.time, message.targetRef, message.senderID)
        # Response
        self.send_message_ackNack(message, "ack")

    def received_message_ackNack(self, message):
        for sent_mes in self.info_messageSent.getList():
            sent_mes.add_ACK_NACK(message)

    def makePredictions(self, method, target):
        # TODO: make factory method instead of checking method maybe
        if method == 1:
            predictor = LinearPrediction()
        predictedPos = predictor.nextPositions(target)

