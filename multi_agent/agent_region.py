import numpy as np
import matplotlib.pyplot as plt
"""
        Class use to detect the derministic region of action from different cameras

        :param
        - room, an object Room that describe the room itself
        - factor, room discretation from 1 to infinite. The bigger the number, the faster the computation will be (less precision).
"""
class AgentRegion():


    def __init__(self,room,factor = 3):
        self.room = room

        '''Mesh from the map'''
        self.nx, self.ny = (room.coord[2], room.coord[3])
        x = np.linspace(0, self.nx, int((self.nx + 1)/factor))
        y = np.linspace(0, self.ny, int((self.ny + 1)/factor))
        self.xv, self.yv = np.meshgrid(x, y)

        '''List from the camera'''
        self.list_camera = []
        for agent in room.agentCams:
            self.list_camera.append(agent.cam)

        '''Data save from each camera - written (camID,res)'''
        self.distances = []
        self.angle_view = []
        self.angle_view_and_obstruction = []

        '''Data representing the map after computation '''
        self.minimum_id_in_view = np.ones(self.xv.shape)*1000000000
        self.minimum_dist_in_view = np.ones(self.xv.shape)*1000000000
        self.id_in_view = np.ones(self.xv.shape)*1000000000
        self.coverage = np.ones(self.xv.shape)*1000000000



    """
            :param
            - factor, room discretation from 1 to infinite. The bigger the number, the faster the computation will be (less precision).

            :return
            - Fill all the table that contains information from the map 
    """
    def compute(self,factor = 3):
        '''Mesh from the map'''
        self.nx, self.ny = (self.room.coord[2], self.room.coord[3])
        x = np.linspace(0, self.nx, int((self.nx + 1) / factor))
        y = np.linspace(0, self.ny, int((self.ny + 1) / factor))
        self.xv, self.yv = np.meshgrid(x, y)

        '''Initialisation '''
        self.minimum_id_in_view = np.ones(self.xv.shape)*1000000000
        self.minimum_dist_in_view = np.ones(self.xv.shape)*1000000000
        self.id_in_view = np.ones(self.xv.shape)*1000000000
        self.coverage = np.ones(self.xv.shape)*1000000000

        '''Required for the computation below'''
        self.find_angle_view_and_obstruction()

        '''Computation'''
        (self.minimum_id_in_view,self.minimum_dist_in_view,self.id_in_view) = self.define_region_covered_by_cams()
        self.coverage = self.define_region_covered_by_numberOfCams()

    """
        :param
        - None
        
        :return (minimum_id_in_view, minimum_dist_in_view,id_in_view)
        - minimum_id_in_view = give the id of the cam in charge for the point x,y from the grid
        - minimum_dist_in_view = give the closest distance to a cam for the point x,y from the grid
        - id_in_view = all the cam that can see the point x,y (! NOT WORKING YET)
    """
    def define_region_covered_by_cams(self):
        '''Initialisation'''
        minimum_dist_in_view = np.ones(self.xv.shape)*1000000000
        minimum_id_in_view = np.ones(self.xv.shape)*-1
        id_in_view = np.chararray(self.xv.shape,itemsize=self.room.agentCamNumber+5)
        result = np.ones(self.xv.shape)*-1
        (i_tot, j_tot) = result.shape

        '''Compute array needed after'''
        self.find_distance_to_each_cam()

        '''Computation for every cam, we need to check every distance'''
        for (camID,res)  in self.angle_view_and_obstruction:
            for (camID_dist,distance) in self.distances:
                if(camID == camID_dist):
                    res_int = (res == 1) #In the visible region

                    '''Check the all array res_int'''
                    for i in range(i_tot):
                        for j in range(j_tot):
                            if res_int[i, j]:
                                'add the point in the list of the camID'
                                #id_in_view[i,j] = str(camID)
                                if distance[i,j] < minimum_dist_in_view[i,j]:
                                    'check if the distance from this cam is the smallest to the point'
                                    minimum_dist_in_view[i,j]=distance[i,j]
                                    minimum_id_in_view[i,j]=camID

        return (minimum_id_in_view, minimum_dist_in_view,id_in_view)

    """
            :param
            - None

            :return covergae
            - coverage = array from the grid size. Contains (int) from 0 to the number of cam.  
                        it gives the information from the number of cam covering the point x,y
    """
    def define_region_covered_by_numberOfCams(self):
        coverage = np.ones(self.xv.shape)*0
        for (camID,res) in self.angle_view_and_obstruction:
            '''addition for each cam from the region cover taking fix obstruction in to account'''
            coverage = coverage + res
        return coverage

    """"
            :param
            - None

            :return
            - None
            
            This fills up the list self.distances, that cointaint the distance from every points from the mesh with respect to the cam
    """
    def find_distance_to_each_cam(self):
        self.distances = []
        for camera in self.list_camera:
            '''taking the position of the camera'''
            px, py = (camera.xc, camera.yc)
            x0 = px * np.ones(self.xv.shape)
            y0 = py * np.ones(self.yv.shape)

            ''' computting the distances, matrix computation !'''
            d = np.power(np.power((self.xv - x0), 2) + np.power((self.yv - y0), 2), 0.5)
            self.distances.append((camera.id, d))

    """"
            :param
            - None

            :return
            - None

            This fills up the list self.angle_view_and_obstruction (see description above)
    """
    def find_angle_view_and_obstruction(self):
        self.angle_view_and_obstruction = []
        for agent in self.room.agentCams:
            '''compute the region of vision from the cam, wihtout obstruction'''
            res = self.find_angle_view(agent.cam)
            '''for every target in the room, suppress obstructed region from the res computed above'''
            res = self.find_obstruction(agent.cam,res)
            '''append the result for each cam'''
            self.angle_view_and_obstruction.append((agent.cam.id,res))

    """"
                :param
                - cam : camera object we want to find the field of vision

                :return
                - fill the list self.angle_view (see description above)

    """
    def find_angle_view(self,cam):
        """
        result = np.ones(self.xv.shape)*0 => camera see nothing
        -> 1 means point x, y is viewed
        -> 0 means point x, y is hidden
        """

        result = np.ones(self.xv.shape)*0
        (i_tot, j_tot) = result.shape
        for i in range(i_tot):
            for j in range(j_tot):
                if cam.is_x_y_inField(self.xv[i,j], self.yv[i,j]):
                    """"Turn the matrix to one when the camera sees the point (x,y)"""
                    result[i,j] = 1
        return result

    """"
                :param
                -None

                :return
                - fill the list self.angle_view (see description above)

    """
    def find_angle_view_allCam(self):
        self.angle_view = []
        for cam in self.list_camera:
            res = self.find_angle_view(cam)
            self.angle_view.append((cam.id, res))

    """"
                :param
                - cam : camera object we want to find the obstructed field of vision
                - result : mesh from the field of the camera. (Computed with find_angle of view)
                           a standart choice could be result = np.ones(self.xv.shape) 
                           -> 1 means point x,y is viewed 
                           -> 0 means point x,y is hidden
                    the function use the map and turn 1 in 0 if the point is not in view.

                :return
                - a array from result's dimension. It gives the camera's field of vision with fix object in the room 
                
    """
    def find_obstruction(self,cam,result):
        return cam. is_in_hidden_zone_allFixTarget_matrix(result,self.xv,self.yv,self.room)







