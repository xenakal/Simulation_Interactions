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
from multi_agent.kalmanPredictionOld import *
from multi_agent.behaviour_detection import *
from multi_agent.room_description import*
from multi_agent.link_target_camera import *
import main

class AgentUser(Agent):

    def __init__(self, idAgent):
        super().__init__(idAgent,"user")
        # Attributes
        self.memory = Memory(idAgent)
        self.behaviour_analysier = TargetBehaviourAnalyser(self.memory)
        self.room_description = Room_Description([255,255,255])
        self.link_target_agent = LinkTargetCamera(self.room_description)

        # Threads
        self.threadRun = 1
        self.my_thread_run = threading.Thread(target=self.thread_run)

        # log_room
        logger_room = logging.getLogger('room' + " agent " + str(self.type) + " " + str(idAgent))
        logger_room.setLevel(logging.INFO)
        # create file handler which log_messages even debug messages
        fh = logging.FileHandler(main.NAME_LOG_PATH + "-" + str(self.type) + " " + str(idAgent) + " " + "-room.txt","w+")
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
        self.message_stat.init_message_static(self.room_description)

    def thread_run(self):
        state = "processData"
        nextstate = state
        my_previousTime = self.room_description.time - 1

        while self.threadRun == 1:
            state = nextstate

            if nextstate == "processData":
                '''Combination of data received and data observed'''
                self.memory.combine_data_userCam()
                '''Modification from the room description'''
                self.room_description.update_target_based_on_memory(self.memory.memory_agent)
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

                self.log_room.info(self.memory.statistic_to_string() + self.message_stat.to_string())
                time.sleep(main.TIME_SEND_READ_MESSAGE)
                nextstate = "processData"
            else:
                print("FSM not working proerly")


    def run_wihout_thread(self):
        pass


    def process_InfoMemory(self, room):
       pass

    def process_Message_sent(self):
        for message_sent in self.info_messageSent.getList():
            if message_sent.is_approved():
                '''Do something'''
                self.info_messageSent.delMessage(message_sent)
            elif message_sent.is_not_approved():
                self.info_messageSent.delMessage(message_sent)

    def process_Message_received(self):
        for rec_mes in self.info_messageReceived.getList():
            if rec_mes.messageType == "memory":
                self.received_message_memory(rec_mes)
            elif rec_mes.messageType == "ack" or rec_mes.messageType == "nack":
                self.received_message_ackNack(rec_mes)

            self.info_messageReceived.delMessage(rec_mes)

    def send_message_ackNack(self, message, typeMessage):
        m = Message_Check_ACK_NACK(self.room_description.time, self.id, self.signature, typeMessage, message.signature,
                                   message.targetRef)
        m.addReceiver(message.senderID, message.senderSignature)
        self.info_messageToSend.addMessage(m)

    def received_message_memory(self, message):
        # Update Info
        s = message.message
        if not (s == ""):
            estimator = TargetEstimator(0,0,0,0,0,0,0,0)

            estimator.parse_string(s)
            self.memory.add_target_estimator(estimator)
            # Response
            self.send_message_ackNack(message, "ack")

    def received_message_ackNack(self, message):
        for sent_mes in self.info_messageSent.getList():
            sent_mes.add_ACK_NACK(message)