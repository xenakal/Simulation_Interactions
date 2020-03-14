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
from multi_agent.kalmanPrediction import *
from multi_agent.room_description import*
from multi_agent.link_target_camera import *
import main

class AgentCam(Agent):

    def __init__(self, idAgent, camera):
        super().__init__(idAgent)
        # Attributes
        self.cam = camera
        self.memory = Memory(idAgent)
        self.room_description = Room_Description(self.color)
        self.link_target_agent = LinkTargetCamera(self.room_description)

        # Threads
        self.threadRun = 1
        self.my_thread_run = threading.Thread(target=self.thread_run)


        # log_room
        logger_room = logging.getLogger('room' + str(idAgent))
        logger_room.setLevel(logging.INFO)
        # create file handler which log_messages even debug messages
        fh = logging.FileHandler(main.NAME_LOG_PATH + str(idAgent) + "-room", "w+")
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

        # not used yet, to be used to quantify the quality of the prediction
        #self.predictionPrecision = {}
        #self.previousPrediction = {}
        #for target in self.myRoom.targets:
            #self.predictionPrecision[target.id] = 0.0
            #self.previousPrediction[target.id] = -1

    def run(self):
        if main.RUN_ON_A_THREAD == 1:
            self.my_thread_run.start()
        else:
            self.run_wihout_thread()

    def clear(self):
        self.threadRun = 0
        while self.my_thread_run.is_alive():
            pass
        mbox = mailbox.mbox(main.NAME_MAILBOX + str(self.id))
        mbox.close()

    def init_and_set_room_description(self,room):
        self.room_description.init(room)
        self.link_target_agent = LinkTargetCamera(self.room_description)
        self.message_stat.init_message_static(self.room_description)

    def thread_run(self):
        """
               One of the two main threads of an agent.
               """
        state = "takePicture"
        nextstate = state
        my_previousTime = self.room_description.time - 1

        while self.threadRun == 1:
            state = nextstate

            if state == "takePicture":
                picture = self.cam.run()
                time.sleep(main.TIME_PICTURE)

                if not self.cam.isActivate():
                    nextstate = "takePicture"
                    time.sleep(0.3)
                else:
                    if my_previousTime != self.room_description.time:  # Si la photo est nouvelle
                        my_previousTime = self.room_description.time

                        for targetElem in picture:
                            self.memory.set_current_time(self.room_description.time)
                            try:
                                target = targetElem[0]

                                if main.INCLUDE_ERROR and not (target.label =="fix"):
                                    erreurX = int(np.random.normal(scale=main.STD_MEASURMENT_ERROR, size=1))
                                    erreurY = int(np.random.normal(scale=main.STD_MEASURMENT_ERROR, size=1))
                                else:
                                    erreurX = 0
                                    erreurY = 0

                                self.memory.add_create_target_estimator(self.room_description.time, self.id, target.id,target.xc+erreurX, target.yc+erreurY, target.size, True)
                            except  AttributeError:
                                print("fichier agent caméra ligne 94: oupsi un problème")

                        self.log_room.info(self.memory.statistic_to_string() + self.message_stat.to_string())
                    nextstate = "processData"  # A voir si on peut améliorer les prédictions avec les mess recu

            elif nextstate == "processData":
                '''Combination of data received and data observed'''
                self.memory.combine_data()
                '''Modification from the room description'''
                self.room_description.update_target_based_on_memory(self.memory.memory_agent)
                '''Computation of the camera that should give the best view, according to map algorithm'''
                self.link_target_agent.update_link_camera_target()
                self.link_target_agent.compute_link_camera_target()
                '''Descision of the messages to send'''
                self.process_InfoMemory(self.room_description)
                nextstate = "communication"

            elif state == "communication":
                '''Suppression of unusefull messages in the list'''
                self.info_messageSent.removeMessageAfterGivenTime(self.room_description.time, 30)
                self.info_messageReceived.removeMessageAfterGivenTime(self.room_description.time, 30)
                '''Message are send (Mailbox)'''
                self.sendAllMessage()
                '''Read messages received'''
                self.recAllMess()
                '''Prepare short answers'''
                self.process_Message_received()
                '''Find if other agents reply to a previous message'''
                self.process_Message_sent()

                time.sleep(main.TIME_SEND_READ_MESSAGE)
                nextstate = "takePicture"
            else:
                print("FSM not working proerly")

    def run_wihout_thread(self):
       print("not working yet")


    def process_InfoMemory(self, room):
        for target in room.targets:
            liste = self.memory.memory_agent.get_target_list(target.id)
            if len(liste) > 0:
                pass
                self.send_message_memory(liste[len(liste) - 1])

    def process_Message_sent(self):
        for message_sent in self.info_messageSent.getList():
            if message_sent.is_approved():
                if message_sent.messageType == "request":
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
        m = Message_Check_ACK_NACK(self.room_description.time, self.id, self.signature, "request", information, target)
        if len(receivers) == 0:
            for agent in self.room_description.agentCams:
                if agent.id != self.id:
                    m.addReceiver(agent.id, agent.signature)
        else:
            for receiver in receivers:
                m.addReceiver(receiver[0], receiver[1])

        cdt1 = self.info_messageToSend.isMessageWithSameTypeSameAgentRef(m)
        cdt2 = self.info_messageSent.isMessageWithSameTypeSameAgentRef(m)
        if not cdt1 and not cdt2:
            self.info_messageToSend.addMessage(m)

    def send_message_memory(self,memory, receivers=None):
        if receivers is None:
            receivers = []
        s = memory.to_string()
        s = s.replace("\n", "")
        s = s.replace(" ", "")

        m = Message_Check_ACK_NACK(self.room_description.time, self.id, self.signature, "memory", s, memory.target_ID)
        if len(receivers) == 0:
            for agent in self.room_description.agentCams:
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
        m = Message_Check_ACK_NACK(self.room_description.time, self.id, self.signature, "locked", message.signature,
                                   message.targetRef)
        if len(receivers) == 0:
            for agent in self.room_description.agentCams:
                if agent.id != self.id:
                    m.addReceiver(agent.id, agent.signature)
        else:
            for receiver in receivers:
                m.addReceiver(receiver[0], receiver[1])

        self.info_messageToSend.addMessage(m)

    def send_message_ackNack(self, message, typeMessage):
        m = Message_Check_ACK_NACK(self.room_description.time, self.id, self.signature, typeMessage, message.signature,
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
            estimator = TargetEstimator(0,0,0,0,0,0,0,0)

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

    def makePredictions(self, method, targetIdList):
        """
        :param targetList -- list of targets IDs: the return list will have an entry for each element of this list
        :return a list of lists: [ [NUMBER_OF_PREDICTIONS*[x_estimated, y_estimated] ],[],...] (len = len(targetIdList)
        """
        if method == 1:
            predictor = LinearPrediction(self.memory, main.TIME_PICTURE)
        elif method == 2:
            predictor = KalmanPrediction(self.memory, main.TIME_PICTURE)
        else:
            predictor = LinearPrediction(self.memory, main.TIME_PICTURE)

        predictions = predictor.makePredictions(targetIdList)

        return predictions

    def predictOcclusions(self, predictions, targetIdList):
        """

        :param predictions: list of lists, each of which contains the predicted positions of the targets in targetIdList
        :param targetIdList: list of targetId's
        :return: list containing the targets that are going to be occluded based on predictions
        """

        occludedTargets = []
        for index, futurePosList in enumerate(predictions):
            for pos in futurePosList:
                if self.notInView(pos):
                    occludedTargets.append(targetIdList[index])
                    break

        return occludedTargets

    def notInView(self, position):
        """
        :param position: [x, y]
        :return: true if the position is seen by the agent, false otherwise
        """
        # TODO
        return self.cam.posInField(position)

