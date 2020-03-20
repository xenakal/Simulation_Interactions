import threading
from my_utils.to_csv import*
# from elements.room import*
import multi_agent.elements.room
from multi_agent.agent.agent import *
from multi_agent.tools.memory import *
from multi_agent.communication.message import *
import constants


class AgentInteractingWithRoom(Agent):
    """
        Class AgentInteractingWithRoom extend Agent.

        Description :

            :param
                1. (int) id                              -- numerical value to recognize the Agent
                2. (AgentType) type                      -- to distinguish the different agent
                3. ((int),(int),(int)) color             -- color representation for the GUI

            :attibutes
                -- IN Agent
                1. (int) id                                     -- numerical value to recognize the Agent
                2. (int) signature                              -- numerical value to identify the Agent, random value
                3. (AgentType) type                             -- to distinguish
                                                                    the different agent
                4. ((int),(int),(int)) color                    -- color representation for the GUI
                5. (ListMessage) info_message_sent              -- list containing all the messages sent
                6. (ListMessage) info_message_received          -- list containing all the messages received
                7. (ListMessage) info_message_to_send           -- list containing all the messages to send
                8. (AgentStatistic) message_statistic           -- object to compute how many messages are sent and
                                                                   received

                ---NEW
                9. (Memory) memory                              -- object to deal with TargetEstimator
               10. (RoomRepresentation) room_representation     -- object to reconstruct the room
               11. (int) thread_is_running                      -- runnig if 1, else stop
               12. (thread) main_thread                         -- thread

            :notes
                fells free to write some comments.
    """

    def __init__(self, id, type_agent, color=0):
        super().__init__(id, type_agent, color)

        "Attibutes"
        self.memory = Memory(id)
        self.room_representation = multi_agent.elements.room.RoomRepresentation(self.color)

        "Create his own thread"
        self.thread_is_running = 1
        self.main_thread = threading.Thread(target=self.thread_run)

        # log_room
        logger_room = logging.getLogger('room' + " agent " + str(self.type) + " " + str(id))
        logger_room.setLevel(logging.INFO)
        # create file handler which log_messages even debug messages
        fh = logging.FileHandler(
            constants.NAME_LOG_PATH + "-" + str(self.type) + " " + str(id) + " " + "-room.txt",
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

    def init_and_set_room_description(self, room):
        """
            :description
                1. set the RoomDescription
                2. set the AgentStatistic

            :param
                1. (Room) room    -- To set up the RoomDescription

        """
        self.room_representation.init_RoomRepresentation(room)
        self.message_statistic.init_message_static(self.room_representation)

    def run(self):
        """
            :description
                1. Function to call to run/start the agent
        """
        if constants.RUN_ON_A_THREAD == 1:
            self.main_thread.start()
        else:
            self.run_wihout_thread()

    def clear(self):
        """
            :description
                1. Function to call to stop the agent
        """
        "Save data"
        if constants.SAVE_DATA:
            print("Saving data:")
            save_in_csv_file_dictionnary("data_saved/data/memory_all_agent/agent"+str(self.id),self.memory.memory_all_agent.to_csv())
            save_in_csv_file_dictionnary("data_saved/data/memory_agent/agent" + str(self.id), self.memory.memory_agent.to_csv())
        "Clear"
        self.thread_is_running = 0
        while self.main_thread.is_alive():
            pass
        mbox = mailbox.mbox(constants.NAME_MAILBOX + str(self.id))
        mbox.close()

    def thread_run(self):
        """ interface """
        pass

    def run_wihout_thread(self):
        """ interface """
        pass

    def process_information_in_memory(self):
        """ interface """
        pass

    def process_message_sent(self):
        """
            :description
                1. Association from ack and nack received to sent messages
        """
        for message_sent in self.info_message_sent.get_list():
            if message_sent.is_approved():
                '''Do something'''
                self.info_message_sent.del_message(message_sent)
            elif message_sent.is_not_approved():
                self.info_message_sent.del_message(message_sent)

    def process_message_received(self):
        """
            :description
                1. Dispatsching to deal with multiple message given the type
        """
        for rec_mes in self.info_message_received.get_list():
            if rec_mes.messageType == "memory":
                self.received_message_targetEstimator(rec_mes)
            elif rec_mes.messageType == "ack" or rec_mes.messageType == "nack":
                self.received_message_ack_nack(rec_mes)

            self.info_message_received.del_message(rec_mes)

    def send_message_targetEstimator(self, memory, receivers=None):
        """
            :description
                1. Create a message based on a TargetEstimator
                2. Place it in the list message_to_send

            :param
                1. (TargetEstimator) targetEstimator -- TargetEstimator, see the class
                2. (list) receivers                  -- [[receiver_id,receiver_signature], ... ], data to
                                                        tell to whom to send the message.

        """

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

        cdt1 = self.info_message_to_send.is_message_with_same_message(m)
        if not cdt1:
            self.info_message_to_send.add_message(m)

    def send_message_ack_nack(self, message, type_message):
        """
            :description
                1. Reply to a mesage using a ack or a nack
                ack = OK, nack = not OK

            :param
                1. (Message) message      -- Response according this message
                2. (string) type_message  -- "ack","nack" either OK or not OK

        """
        m = MessageCheckACKNACK(self.room_representation.time, self.id, self.signature, type_message,
                                message.signature,
                                message.targetRef)
        m.add_receiver(message.sender_id, message.sender_signature)
        self.info_message_to_send.add_message(m)

    def received_message_targetEstimator(self, message):
        """
            :description
                1. Create a new TargetEstimator from the string description received
                2. Add the new TargetEstimator in the memory

            :param
                1. (Message) message  -- Message received

        """
        s = message.message
        if not (s == ""):
            estimator = TargetEstimator(0, 0, 0, 0, 0, 0, 0, 0, )
            estimator.parse_string(s)
            self.memory.add_target_estimator(estimator)
            self.send_message_ack_nack(message, "ack")

    def received_message_ack_nack(self, message):
        """
            :description
                1. Create a new TargetEstimator from the string description received
                2. Add the new TargetEstimator in the memory

            :param
                1. (Message) message --  Message received

        """
        for sent_mes in self.info_message_sent.get_list():
            sent_mes.add_ack_nack(message)
