import mailbox
import logging
from multi_agent.communication.message import *
import constants
import io


class AgentType:
    AGENT_CAM = 0
    AGENT_USER = 100

class Agent:
    """
        Class Agent.

        Description : Object abble to send and receive message from other agent via Mailbox

            :param
                1. (int) id                              -- numerical value to recognize the Agent
                2. (AgentType) type                      -- to distinguish the different agent
                3. ((int),(int),(int)) color             -- color representation for the GUI

            :attibutes
                1. (int) id                              -- numerical value to recognize the Agent
                2. (int) signature                       -- numerical value to identify the Agent, random value
                3. (AgentType) type                      -- to distinguish the different agent
                4. ((int),(int),(int)) color             -- color representation for the GUI
                5. (ListMessage) info_message_sent       -- list containing all the messages sent
                6. (ListMessage) info_message_received   -- list containing all the messages received
                7. (ListMessage) info_message_to_send    -- list containing all the messages to send
                8. (AgentStatistic) message_statistic    -- object to compute how many messages are sent and received

            :notes
                fells free to write some comments.
    """

    def __init__(self, id, type, color=0):
        """Initialisation"""

        "Attributes"
        self.id = id + type
        self.signature = int(random.random() * 10000000000000000) + 100  # always higher than 100
        self.type = type
        self.color = color

        "Communication"
        self.info_message_sent = ListMessage("Sent")
        self.info_message_received = ListMessage("Received")
        self.info_message_to_send = ListMessage("ToSend")
        self.message_statistic = AgentStatistic(id)

        "Mailbox creation to receive message"
        mbox = mailbox.mbox(constants.NAME_MAILBOX + str(self.id))
        mbox.clear()

        "Default values"

        if color == 0:
            r = random.randrange(20, 230, 1)
            g = random.randrange(20, 230, 1)
            b = random.randrange(20, 255, 1)
            self.color = (r, g, b)

        "Logger to keep track of every send and received messages"
        # create logger_message with 'spam_application'
        logger_message = logging.getLogger('agent' + str(self.type) + " " + str(self.id))
        logger_message.setLevel(logging.INFO)
        # create file handler which log_messages even debug messages
        fh = logging.FileHandler(constants.NAME_LOG_PATH + "-" + str(self.type) + " " + str(self.id) + "-messages.txt",
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
        logger_message.addHandler(fh)
        logger_message.addHandler(ch)
        self.log_message = logger_message

    #
    def parse_received_messages(self, m):
        """
            :description
                1. Create an object Message from its string description.
                2. If received (statistic error possible), append it to info_message_received and update stat.

            :param
                1. (string) m -- string representation of a message, see method to_sting in class Message

        """

        "reconstruction from the object"
        rec_mes = Message(0, 0, 0, 0, 0)
        rec_mes.parse_string(m)

        "random value to modelise that some message are not received"
        random_value = np.random.normal(loc=0, scale=constants.STD_RECEIVED)
        if -constants.SEUIL_RECEIVED < random_value < constants.SEUIL_RECEIVED:
            self.message_statistic.count_message_received(rec_mes.sender_id)
            self.info_message_received.add_message(rec_mes)
            self.log_message.info('RECEIVED : \n' + rec_mes.to_string())

    def receive_messages(self):
        """
            :description
               1. Check the Mailbox file to see if it got a message
               2. Call parse_received_message(m) to deal with new messages.

        """
        succes = -1
        mbox_rec = mailbox.mbox(constants.NAME_MAILBOX + str(self.id))
        try:
            mbox_rec.lock()
            keys = mbox_rec.keys()
            try:
                succes = 0
                for key in keys:
                    m = mbox_rec.get_string(key)

                    if m != "":
                        self.parse_received_messages(m)

                        if succes == 0:
                            mbox_rec.remove(key)
                            mbox_rec.flush()
            finally:
                mbox_rec.unlock()

        except mailbox.ExternalClashError:
            self.log_message.warning("Not possible to read messages")
        except FileExistsError:
            self.log_message.warning("Mailbox file error RECEIVE")
        except PermissionError:
            self.log_message.warning("Windows error")

        return succes

    def send_messages(self):
        """
            :description
              1. Send all the message in the list info_message_to_send
              2. if send remove it from the list and place it in the list info_message_sent
        """

        for message in self.info_message_to_send.get_list():
            isSend = self.send_one_message(message)
            if isSend == 0:
                self.info_message_to_send.del_message(message)
                self.info_message_sent.add_message(message)

    def send_one_message(self, m):
        """
            :description
                1. Send the message to every receiver.

            :param
                1. (Message) m -- Message to send.

        """
        succes = -1
        for receiver in m.remaining_receiver:
            try:
                mbox = mailbox.mbox(constants.NAME_MAILBOX + str(receiver[0]))
                mbox.lock()
                try:
                    mbox.add(m.to_string())
                    self.message_statistic.count_message_send(receiver[0])

                    mbox.flush()
                    m.notify_send_to(receiver[0], receiver[1])
                    if m.is_message_sent_to_every_receiver():
                        self.log_message.info('SEND     : \n' + m.to_string())
                        succes = 0
                    else:
                        succes = 1
                finally:
                    mbox.unlock()

            except mailbox.ExternalClashError:
                self.log_message.warning("Not possible to send messages")
            except FileExistsError:
                self.log_message.warning("Mailbox file error SEND")
            except PermissionError:
                self.log_message.warning("Windows error")
            except FileNotFoundError:
                self.log_message.warning("Mailbox file error SEND")
            except io.UnsupportedOperation:
                self.log_message.warning("io Unsupported op")

        return succes

    ############################
    # Other
    ############################

    def clear(self):
        """
            :description
                close the Mailbox at the end of usage.
        """
        mbox = mailbox.mbox(constants.NAME_MAILBOX + str(self.id))
        mbox.close()

    def process_information_in_memory(self):
        """interface"""
        pass

    def process_message_sent(self):
        """interface"""
        pass

    def process_message_received(self):
        """interface"""
        pass


class AgentStatistic:
    """
        Class AgentStatistic.

        Description : Class to count messages received and sent

            :param
                1. (int) id                              -- numerical value to recognize the Agent
                2. (list) send_message_statistic         -- [[agent.id,int],...], keep track of message send to an agent
                3. (list) received_message_statistic     -- [[agent.id,int],...], keep track of message received from
                                                            an agent

            :attibutes
                1. (int) id                              -- numerical value to recognize the Agent

            :notes
                !! Dynamic allocation not possible here, need to be added, but not very usefull for us.
    """

    def __init__(self, id):
        self.id = id
        self.send_message_statistic = []
        self.receive_message_statistic = []

    def init_message_static(self, room):
        """
            :description
                initialise the table for every agent in the room => Can not add a new agent once created !!

            :param
                1. (Room) room --
        """

        tab0 = []
        tab1 = []
        for agent in room.active_AgentCams_list:
            tab0.append([agent.id, 0])
            tab1.append([agent.id, 0])

        for agent in room.active_AgentUser_list:
            tab0.append([agent.id, 0])
            tab1.append([agent.id, 0])

        self.send_message_statistic = tab0.copy()
        self.receive_message_statistic = tab1.copy()

    def get_number_message_sent(self, agent):
        """
            :param
                1. (Agent) agent -- Agent, see class above

            :return
                number of message sent to the agent
                if agent not found => None
        """
        for element in self.send_message_statistic:
            if element[0] == agent.id:
                return element[1]

    def get_number_message_received(self, agent):
        """
            :param
                1. (Agent) agent -- Agent, see class above

            :return
                number of message received from the agent
                if agent not found => None
        """
        for element in self.receive_message_statistic:
            if element[0] == agent.id:
                return element[1]

    def count_message_send(self, receiver_id):
        """
            :description
                update the list send_message_statistic

            :param
                1. (int) receiver_id --
        """
        for element in self.send_message_statistic:
            if element[0] == receiver_id:
                element[1] = element[1] + 1

    def count_message_received(self, sender_id):
        """
            :description
                update the list send_message_statistic

            :param
                1. (int) sender_id --
        """
        for element in self.receive_message_statistic:
            if element[0] == sender_id:
                element[1] = element[1] + 1

    def to_string(self):
        """
                 :return / modify vector
                        1. (string)  -- description of the list
        """
        s = "Statistic message \n"
        for element in self.send_message_statistic:
            if element[0] != self.id:
                s = s + "Sender agent: " + str(self.id) + " receiver agent: " + str(
                    element[0]) + ", # messages = " + str(element[1]) + "\n"
        for element in self.receive_message_statistic:
            if element[0] != self.id:
                s = s + "Receiver agent: " + str(self.id) + " sender agent: " + str(
                    element[0]) + ", # messages = " + str(element[1]) + "\n"
        return s


if __name__ == "__constants__":
    pass
