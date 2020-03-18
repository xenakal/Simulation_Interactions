import threading
import mailbox
import logging
from multi_agent.elements.target import *
# from elements.room import*
import multi_agent.elements.room
from multi_agent.agent.agent import *
from multi_agent.tools.memory import *
from multi_agent.communication.message import *
from multi_agent.prediction.kalmanPredictionOld import *
from multi_agent.tools.behaviour_detection import *
from multi_agent.tools.link_target_camera import *
import constants


class AgentInteractingWithRoom(Agent):
    def __init__(self, idAgent,type_agent):
        super().__init__(idAgent, type_agent)

        self.memory = Memory(idAgent)
        self.room_representation = multi_agent.elements.room.RoomRepresentation(self.color)

        # Threads
        self.threadRun = 1
        self.my_thread_run = threading.Thread(target=self.thread_run)

        # log_room
        logger_room = logging.getLogger('room' + " agent " + str(self.type) + " " + str(idAgent))
        logger_room.setLevel(logging.INFO)
        # create file handler which log_messages even debug messages
        fh = logging.FileHandler(
            constants.NAME_LOG_PATH + "-" + str(self.type) + " " + str(idAgent) + " " + "-room.txt",
            "w+")
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
        if constants.RUN_ON_A_THREAD == 1:
            self.my_thread_run.start()
        else:
            self.run_wihout_thread()

    def clear(self):
        self.threadRun = 0
        while self.my_thread_run.is_alive():
            pass
        mbox = mailbox.mbox(constants.NAME_MAILBOX + str(self.id))
        mbox.close()

    def init_and_set_room_description(self, room):
        self.room_representation.init_RoomRepresentation(room)
        self.message_stat.init_message_static(self.room_representation)

    def thread_run(self):
        print("not implemented")

    def run_wihout_thread(self):
        pass

    def process_InfoMemory(self, room):
        pass

    def process_Message_sent(self):
        for message_sent in self.info_messageSent.get_list():
            if message_sent.is_approved():
                '''Do something'''
                self.info_messageSent.del_message(message_sent)
            elif message_sent.is_not_approved():
                self.info_messageSent.del_message(message_sent)

    def process_Message_received(self):
        for rec_mes in self.info_messageReceived.get_list():
            if rec_mes.messageType == "memory":
                self.received_message_memory(rec_mes)
            elif rec_mes.messageType == "ack" or rec_mes.messageType == "nack":
                self.received_message_ackNack(rec_mes)

            self.info_messageReceived.del_message(rec_mes)

    def send_message_memory(self, memory, receivers=None):
        if receivers is None:
            receivers = []
        s = memory.to_string()
        s = s.replace("\n", "")
        s = s.replace(" ", "")

        m = MessageCheckACKNACK(self.room_representation.time, self.id, self.signature, "memory", s,
                                memory.target_id)
        if len(receivers) == 0:
            for agent in self.room_representation.active_AgentCams_list:
                if agent.id != self.id:
                    m.add_receiver(agent.id, agent.signature)
        else:
            for receiver in receivers:
                m.add_receiver(receiver[0], receiver[1])

        cdt1 = self.info_messageToSend.is_message_with_same_message(m)
        if not cdt1:
            self.info_messageToSend.add_message(m)

    def send_message_ackNack(self, message, typeMessage):
        m = MessageCheckACKNACK(self.room_representation.time, self.id, self.signature, typeMessage,
                                message.signature,
                                message.targetRef)
        m.add_receiver(message.sender_id, message.sender_signature)
        self.info_messageToSend.add_message(m)

    def received_message_memory(self, message):
        # Update Info
        s = message.message
        if not (s == ""):
            estimator = TargetEstimator(0, 0, 0, 0, 0, 0, 0, 0, )

            estimator.parse_string(s)
            self.memory.add_target_estimator(estimator)
            # Response
            self.send_message_ackNack(message, "ack")


    def received_message_ackNack(self, message):
        for sent_mes in self.info_messageSent.get_list():
            sent_mes.add_ack_nack(message)

