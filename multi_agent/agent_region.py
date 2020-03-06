import numpy as np
import matplotlib.pyplot as plt


class AgentRegion():
    """
        Class use to detect the derministic region of action from different cameras

        :param
        """

    def __init__(self,room,facteur = 3):
        self.room = room
        self.nx, self.ny = (room.coord[2],room.coord[3])

        x = np.linspace(0, self.nx, int((self.nx + 1)/facteur))
        y = np.linspace(0, self.ny, int((self.ny + 1)/facteur))
        self.xv, self.yv = np.meshgrid(x, y)

        self.list_camera = []
        for agent in room.agentCams:
            self.list_camera.append(agent.cam)

        self.distances = []
        self.angle_view = []
        self.angle_view_and_obstruction = []

        self.mimimum_id = np.ones(self.xv.shape)*1000000000
        self.minimum_distance = np.ones(self.xv.shape)*1000000000
        self.minimum_id_in_view = np.ones(self.xv.shape)*1000000000
        self.minimum_dist_in_view = np.ones(self.xv.shape)*1000000000
        self.id_in_view = np.ones(self.xv.shape)*1000000000
        self.coverage = np.ones(self.xv.shape)*1000000000

    def find_mimimum_distance(self):
        #require to compute all the distance from every cam first
        self.find_distance_to_each_cam()

        minimum_id = np.ones(self.xv.shape)*1000000000
        minimum_dist = np.ones(self.xv.shape)*1000000000

        for (camID,distance) in self.distances:
            result = minimum_dist > distance
            (i_tot,j_tot) =  result.shape
            for i in range(i_tot):
                for j in range(j_tot):
                   if result[i,j]:
                      minimum_dist[i,j] = distance[i,j]
                      minimum_id[i, j] = camID

        self.minimum_distance = minimum_dist
        self.minimum_distance = minimum_dist

        return(minimum_id,minimum_dist)

    def define_region_covered_by_cams(self):
        self.find_distance_to_each_cam()
        self.find_angle_view_and_obstruction()

        minimum_dist_in_view = np.ones(self.xv.shape)*1000000000
        minimum_id_in_view = np.ones(self.xv.shape)*-1
        id_in_view = np.chararray(self.xv.shape,itemsize=self.room.agentCamNumber+5)
        result = np.ones(self.xv.shape)*-1
        (i_tot, j_tot) = result.shape

        for (camID,res)  in self.angle_view_and_obstruction:
            for (camID_dist,distance) in self.distances:
                if(camID == camID_dist):
                    res_int = (res == 1) #In the visible region
                    for i in range(i_tot):
                        for j in range(j_tot):
                            if res_int[i, j]:
                                #id_in_view[i,j] = str(camID)
                                #print(id_in_view[i,j])
                                if distance[i,j] < minimum_dist_in_view[i,j]:
                                    minimum_dist_in_view[i,j]=distance[i,j]
                                    minimum_id_in_view[i,j]=camID

        self.minimum_dist_in_view = minimum_dist_in_view
        self.minimum_id_in_view = minimum_id_in_view
        self.id_in_view = id_in_view

        return (minimum_id_in_view, minimum_dist_in_view,id_in_view)


    def define_region_covered_by_numberOfCams(self):
        self.find_angle_view_and_obstruction()
        result = np.ones(self.xv.shape)*0

        for (camID,res) in self.angle_view_and_obstruction:
            result = result + res

        self.coverage = result
        return result

    def find_distance_to_each_cam(self):
        for camera in self.list_camera:
            # take camera position
            px, py = (camera.xc, camera.yc)
            x0 = px * np.ones(self.xv.shape)
            y0 = py * np.ones(self.yv.shape)

            # comptute the distances
            d = np.power(np.power((self.xv - x0), 2) + np.power((self.yv - y0), 2), 0.5)
            self.distances.append((camera.id, d))

    def find_angle_view_and_obstruction(self):
        for agent in self.room.agentCams:
            res = self.find_angle_view(agent.cam)
            res = self.find_obstruction(agent.cam,res)
            self.angle_view_and_obstruction.append((agent.cam.id,res))

    def find_angle_view(self,cam):
        result = np.ones(self.xv.shape)*0
        (i_tot, j_tot) = result.shape
        for i in range(i_tot):
            for j in range(j_tot):
                if cam.is_x_y_inField(self.xv[i,j], self.yv[i,j]):
                    result[i,j] = 1
        return result

    def find_angle_view_allCam(self):
        for cam in self.list_camera:
            res = self.find_angle_view(cam)
            self.angle_view.append((cam.id, res))

    def find_obstruction(self,cam,result):
        return cam. is_in_hidden_zone_allFixTarget_matrix(result,self.xv,self.yv,self.room)







