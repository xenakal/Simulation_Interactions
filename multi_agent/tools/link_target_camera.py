import numpy as np

class LinkTargetCamera():
    """

                :param
                - room, an object Room that describe the room itself
    """

    def __init__(self, room):
        self.room = room
        self.link_camera_target = []
        '''List from the camera'''
        self.list_camera = []
        for agent in room.active_AgentCams_list:
            self.list_camera.append(agent.cam)

    def update_link_camera_target(self):
        for target in self.room.active_Target_list:
            is_in_list = False
            for item in self.link_camera_target:
                (targetID,camID,distance) = item
                if targetID == target.id:
                    is_in_list = True
                    break

            if not is_in_list:
                self.link_camera_target.append((target.id,-1,10000000))

    def reset_distance(self):
        for item in self.link_camera_target:
            (targetID, camID, distance) = item
            self.link_camera_target.remove(item)
            self.link_camera_target.append((targetID, -1, 1000000000))


    def compute_link_camera_target(self):
        self.reset_distance()

        for camera in self.list_camera:
            for target in self.room.active_Target_list:
                """Ici dans le calcul au lieu d'utiliser les positions actuelles on peut aussi utiliser les prédictions"""

                if not camera.is_in_hidden_zone_all_targets(target.xc,target.yc,self.room) and camera.is_x_y_in_field_not_obstructed(target.xc,target.yc):
                    distance_to_target = np.power(np.power((camera.xc - target.xc), 2) + np.power((camera.yc - target.yc), 2), 0.5)
                    for item in self.link_camera_target:
                        (targetID,camID,distance) = item

                        if  targetID == target.id and distance_to_target < distance:
                                self.link_camera_target.remove(item)
                                self.link_camera_target.append((targetID,camera.id,distance_to_target))


    def is_in_charge(self,target_id,agent_id):
        for item in self.link_camera_target:
            (targetID, camID, distance) = item
            if targetID == target_id and camID == agent_id:
                return True
        return False





