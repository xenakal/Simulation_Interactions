import threading
import mailbox
import logging
from multi_agent.elements.target import *
# from elements.room import*
import multi_agent.elements.room
from multi_agent.agent.agent_interacting_room import *
from multi_agent.tools.memory import *
from multi_agent.communication.message import *
from multi_agent.prediction.kalmanPredictionOld import *
from multi_agent.tools.behaviour_detection import *
from multi_agent.tools.link_target_camera import *
import constants


class AgentCam(AgentInteractingWithRoom):
    def __init__(self, idAgent, camera):
        super().__init__(idAgent, "camera")
        # Attributes
        self.cam = camera
        self.behaviour_analysier = TargetBehaviourAnalyser(self.memory)
        self.link_target_agent = LinkTargetCamera(self.room_representation)


    def init_and_set_room_description(self, room):
        super().init_and_set_room_description(room)
        self.link_target_agent = LinkTargetCamera(self.room_representation)

    def thread_run(self):
        """
               One of the two constants threads of an agent.
        """
        state = "takePicture"
        nextstate = state
        my_previousTime = self.room_representation.time - 1

        while self.threadRun == 1:
            state = nextstate

            if state == "takePicture":

                '''Input from the agent, here the fake room'''
                picture = self.cam.run()
                time.sleep(constants.TIME_PICTURE)

                '''Allows to simulate crash of the camera'''
                if not self.cam.is_camera_active():
                    nextstate = "takePicture"
                    time.sleep(0.3)
                else:
                    '''If the camera is working and we have a new picture, then the informations are stored in 
                    memory. '''
                    if my_previousTime != self.room_representation.time:  # Si la photo est nouvelle
                        my_previousTime = self.room_representation.time
                        for targetCameraDistance in picture:
                            self.memory.set_current_time(self.room_representation.time)
                            try:
                                target = targetCameraDistance.target
                                '''Simulation from noise on the target's position '''
                                if constants.INCLUDE_ERROR and not (target.type == "fix"):
                                    erreurX = int(np.random.normal(scale=constants.STD_MEASURMENT_ERROR, size=1))
                                    erreurY = int(np.random.normal(scale=constants.STD_MEASURMENT_ERROR, size=1))
                                else:
                                    erreurX = 0
                                    erreurY = 0

                                self.memory.add_create_target_estimator(self.room_representation.time, self.id,
                                                                        self.signature, target.id, target.signature,
                                                                        target.xc + erreurX, target.yc + erreurY,
                                                                        target.radius)

                            except AttributeError:
                                print("fichier agent caméra ligne 134: oupsi un problème")

                    nextstate = "processData"  # A voir si on peut améliorer les prédictions avec les mess recu

            elif nextstate == "processData":
                '''Combination of data received and data observed'''
                self.memory.combine_data_agentCam()
                '''Modification from the room description'''
                self.room_representation.update_target_based_on_memory(self.memory.memory_agent)
                '''Computation of the camera that should give the best view, according to map algorithm'''
                self.link_target_agent.update_link_camera_target()
                self.link_target_agent.compute_link_camera_target()
                '''Descision of the messages to send'''
                self.process_InfoMemory(self.room_representation)
                nextstate = "communication"

            # TODO: pas mieux de mettre ca avant "processData" ?
            elif state == "communication":
                '''Suppression of unusefull messages in the list'''
                self.info_messageSent.remove_message_after_given_time(self.room_representation.time, 30)
                self.info_messageReceived.remove_message_after_given_time(self.room_representation.time, 30)
                '''Message are send (Mailbox)'''
                self.sendAllMessage()
                '''Read messages received'''
                self.recAllMess()
                '''Prepare short answers'''
                self.process_Message_received()
                '''Find if other agents reply to a previous message'''
                self.process_Message_sent()

                self.log_room.info(self.memory.statistic_to_string() + self.message_stat.to_string())
                time.sleep(constants.TIME_SEND_READ_MESSAGE)
                nextstate = "takePicture"
            else:
                print("FSM not working proerly")

    def process_InfoMemory(self, room):
        for target in room.active_Target_list:
            """
                ---------------------------------------------------------------------------------------------
                Memory analysis: 
                    -> Behaviour
                        - detection from moving, stop , changing state targest
                        - detection from target leaving the field of the camera
                ---------------------------------------------------------------------------------------------
            """
            '''Check if the target is moving,stopped or changing from one to the other state'''
            (is_moving, is_stopped) = self.behaviour_analysier.detect_target_motion(target.id, 4, 3, 3)
            '''Check if the target is leaving the cam angle_of_view'''
            (is_in, is_out) = self.behaviour_analysier.is_target_leaving_cam_field(self.cam, target.id, 0, 3)

            """
                ----------------------------------------------------------------------------------------------
                Data to send other cam's agent:
                -----------------------------------------------------------------------------------------------
            """
            '''Send message to other agent'''
            if constants.DATA_TO_SEND == "all":
                memories = self.memory.memory_agent.get_target_list(target.id)
                if len(memories) > 0:
                    last_memory = memories[len(memories) - 1]
                    self.send_message_memory(last_memory)

            elif constants.DATA_TO_SEND == "behaviour":
                '''If the target stop is it because we loose it, or is the target outside from the range ? '''
                pass
                '''Demande de confirmation à un autre agent par exemple'''

            """
               ----------------------------------------------------------------------------------------------
               Data to send user's agent:
               -----------------------------------------------------------------------------------------------
            """

            '''If the target is link to this agent then we send the message to the user'''
            if self.link_target_agent.is_in_charge(target.id, self.id):
                memories = self.memory.memory_agent.get_Target_list(target.id)
                if len(memories) > 0:
                    receivers = []
                    for agent in room.active_AgentUser_list:
                        receivers.append([agent.id, agent.signature])
                    last_memory = memories[len(memories) - 1]

                    '''If the message is to old we don't send it -> target lost'''
                    thresh_time_to_send = 10
                    if self.room_representation.time - last_memory.time_stamp <= thresh_time_to_send:
                        self.send_message_memory(last_memory, receivers)

    def process_Message_sent(self):
        for message_sent in self.info_messageSent.get_list():
            if message_sent.is_approved():
                if message_sent.messageType == "request":
                    self.send_message_locked(message_sent)

                self.info_messageSent.del_message(message_sent)
            elif message_sent.is_not_approved():
                self.info_messageSent.del_message(message_sent)

    def process_Message_received(self):
        super().process_Message_received()
        for rec_mes in self.info_messageReceived.get_list():
            if rec_mes.messageType == "request":
                self.received_message_request(rec_mes)
            elif rec_mes.messageType == "locked":
                self.received_message_locked(rec_mes)

            self.info_messageReceived.del_message(rec_mes)

    def send_message_request(self, information, target, receivers=None):
        if receivers is None:
            receivers = []
        m = MessageCheckACKNACK(self.room_representation.time, self.id, self.signature, "request", information,
                                target)
        if len(receivers) == 0:
            for agent in self.room_representation.agentCams:
                if agent.id != self.id:
                    m.add_receiver(agent.id, agent.signature)
        else:
            for receiver in receivers:
                m.add_receiver(receiver[0], receiver[1])

        cdt1 = self.info_messageToSend.is_message_with_same_type_same_agent_ref(m)
        cdt2 = self.info_messageSent.is_message_with_same_type_same_agent_ref(m)
        if not cdt1 and not cdt2:
            self.info_messageToSend.add_message(m)

    def send_message_locked(self, message, receivers=None):
        if receivers is None:
            receivers = []
        m = MessageCheckACKNACK(self.room_representation.time, self.id, self.signature, "locked", message.signature,
                                message.targetRef)
        if len(receivers) == 0:
            for agent in self.room_representation.agentCams:
                if agent.id != self.id:
                    m.add_receiver(agent.id, agent.signature)
        else:
            for receiver in receivers:
                m.add_receiver(receiver[0], receiver[1])

        self.info_messageToSend.add_message(m)

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

    def received_message_locked(self, message):
        # Update Info
        #
        # Response
        self.send_message_ackNack(message, "ack")


    def get_predictions(self, targetIdList):
        return self.memory.get_predictions(targetIdList)

    def makePredictionsOld(self, method, targetIdList):
        """
        :param targetList -- list of targets IDs: the return list will have an entry for each element of this list
        :return a list of lists: [ [NUMBER_OF_PREDICTIONS*[x_estimated, y_estimated] ],[],...] (len = len(targetIdList)
        """
        if method == 1:
            predictor = LinearPrediction(self.memory, constants.TIME_PICTURE)
        elif method == 2:
            predictor = KalmanPredictionOld(self.memory, constants.TIME_PICTURE)
        else:
            predictor = LinearPrediction(self.memory, constants.TIME_PICTURE)

        predictions = predictor.makePredictions(targetIdList)

        return predictions
