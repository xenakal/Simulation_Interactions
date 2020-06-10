import numpy as np

from src import constants
from src.multi_agent.elements.camera import is_x_y_radius_in_field_not_obstructed, \
    is_in_hidden_zone_fix_targets_matrix_x_y


def create_region(nx, ny, factor=10, x0=0, y0=0):
    x = np.linspace(x0, int(nx),int(nx)*factor)
    y = np.linspace(y0, int(ny),int(nx)*factor)
    xv, yv = np.meshgrid(x, y)
    return xv, yv


class MapRegionStatic:
    """
                Class use to detect the derministic region of action from different cameras

                :param
                - room, an object Room that describe the room itself
                - factor, room discretation from 1 to infinite. The bigger the number, the faster the computation will be (less precision).
    """

    def __init__(self, room):
        self.room = room

        # Mesh from the maps
        self.nx, self.ny = (room.coordinate_room[2], room.coordinate_room[3])
        self.xv, self.yv = create_region(int(self.nx), int(self.ny), 10)

        # Data save from each camera - written always as tuple (camID,res), res is an array from mesh size
        self.distances = []
        self.angle_view = []
        self.angle_view_and_fix_obstruction = []

        self.agent_id_taken_into_acount = []

        self.coverage_percentage = [0,0,0,0,0,0]
        self.n_point = 100

        """
        Data representing the maps after computation, array size from the matrix
        the position in the array i,j refers always to the point i,j in the mesh 
        
        self.minimum_id_in_view, contains the cam ID, that is the clostest from x,y and sees it
        self.minimum_dist_in_view, contains the distances used in the matrix above
        self.id_in_view, contains all the camera int that can see the point x,y
        self.coverage, shows how many cameras see the point x,y
        """

        self.minimum_id_in_view = np.ones(self.xv.shape) * 1000000000
        self.minimum_dist_in_view = np.ones(self.xv.shape) * 1000000000
        self.coverage = np.ones(self.xv.shape) * 1000000000

    def init(self, factor=10, save = False):
        """ Contains every vectors that needs only one computation """
        # Initialisation
        self.minimum_id_in_view = np.ones(self.xv.shape) * 1000000000
        self.minimum_dist_in_view = np.ones(self.xv.shape) * 1000000000
        self.coverage = np.ones(self.xv.shape) * 1000000000

        # Setting the grid to the right size
        (self.xv, self.yv) = create_region(self.nx, self.ny, factor)
        # Compute array needed after
        self.find_distance_to_each_cam()
        # Compute the field of vision not obstructed from each cam
        self.find_angle_view_all_cam()

        # Required for the computation below
        self.find_angle_view_all_cam_and_fix_obstruction()

        self.coverage_percentage = [0,0,0,0,0,0]
        self.n_point = self.nx*factor*self.ny*factor


         # Compute one for those values
        (self.minimum_id_in_view, self.minimum_dist_in_view) = self.define_region_covered_by_cams()
        self.coverage = self.define_region_covered_by_numberOfCams()

        if constants.SAVE_DATA and save:
            np.savetxt(constants.ResultsPath.SAVE_LOAD_DATA_STATIC_REGION + "x_init", self.xv)
            np.savetxt(constants.ResultsPath.SAVE_LOAD_DATA_STATIC_REGION + "y_init", self.yv)
            np.savetxt(constants.ResultsPath.SAVE_LOAD_DATA_STATIC_REGION + "region_init", self.minimum_id_in_view)
            np.savetxt(constants.ResultsPath.SAVE_LOAD_DATA_STATIC_REGION + "coverage_init", self.coverage)


    def update_active_cams(self):
        is_changed_in_agent = False
        "adding new id if needed"
        for agent in self.room.active_AgentCams_list:
            if not agent.id in self.agent_id_taken_into_acount and agent.camera.is_active:
                is_changed_in_agent = True
                self.agent_id_taken_into_acount.append(agent.id)

        "suppressing id if needed"
        agent_id_to_suppress = []
        for agent_id in self.agent_id_taken_into_acount:
            found = False
            for agent in self.room.active_AgentCams_list:
                if agent_id == agent.id and agent.camera.is_active:
                    found = True
                    break
            if not found:
                is_changed_in_agent = True
                agent_id_to_suppress.append(agent_id)

        for agent_id in agent_id_to_suppress:
            self.agent_id_taken_into_acount.remove(agent_id)

        return is_changed_in_agent

    def compute_all_map(self, factor=3,save = False):
        """
        :param
            - factor, room discretation from 1 to infinite. The bigger the number, the faster the computation will be (less precision).

        :return
            - Fill all the table that contains information from the maps
        """

        if self.update_active_cams():
            if constants.SAVE_DATA and save:
                np.savetxt(
                    constants.ResultsPath.SAVE_LOAD_DATA_STATIC_REGION + "region_updated %.02f s" % constants.get_time(),
                    self.minimum_id_in_view)
                np.savetxt(
                    constants.ResultsPath.SAVE_LOAD_DATA_STATIC_REGION + "coverage_updated %.02f s" % constants.get_time(),
                    self.coverage)

            (self.minimum_id_in_view, self.minimum_dist_in_view) = self.define_region_covered_by_cams()
            self.coverage = self.define_region_covered_by_numberOfCams()
            self.define_coverage_percentarge()


    def define_coverage_percentarge(self):
        self.coverage_percentage = [0,0,0,0,0,0]
        (i_tot, j_tot) = self.coverage.shape
        for i in range(i_tot):
            for j in range(j_tot):
                var = self.coverage[i,j]
                if var < 5:
                    self.coverage_percentage[int(var)] += 1
                else:
                    self.coverage_percentage[5] += 1


        self.coverage_percentage = np.array(self.coverage_percentage)/self.n_point*100
        #print("Pourcentage couvert : %s"%self.coverage_percentage)

    def define_region_covered_by_cams(self):
        """
            :param
            - None

            :return (minimum_id_in_view, minimum_dist_in_view,id_in_view)
            - minimum_id_in_view = give the id of the cam in charge for the point x,y from the grid
            - minimum_dist_in_view = give the closest distance to a cam for the point x,y from the grid
            - id_in_view = all the cam that can see the point x,y (! NOT WORKING YET)
        """
        minimum_dist_in_view = np.ones(self.xv.shape) * 1000000000
        minimum_id_in_view = np.ones(self.xv.shape) * -1
        result = np.ones(self.xv.shape) * -1
        (i_tot, j_tot) = result.shape

        '''Computation for every cam, we need to check every distance'''
        for (camID, res) in self.angle_view_and_fix_obstruction:
            for (camID_dist, distance) in self.distances:
                if camID == camID_dist and camID in self.agent_id_taken_into_acount:
                    res_int = (res == 1)  # In the visible region

                    '''Check the all array res_int'''
                    for i in range(i_tot):
                        for j in range(j_tot):
                            if res_int[i, j]:
                                if distance[i, j] < minimum_dist_in_view[i, j]:
                                    'check if the distance from this cam is the smallest to the point'
                                    minimum_dist_in_view[i, j] = distance[i, j]
                                    minimum_id_in_view[i, j] = camID

        return minimum_id_in_view, minimum_dist_in_view

    def define_region_covered_by_numberOfCams(self):
        """
        :param
            - None

        :return covergae
            - coverage = array from the grid size. Contains (int) from 0 to the number of cam.
                        it gives the information from the number of cam covering the point x,y
        """
        coverage = np.ones(self.xv.shape) * 0
        for (camID, res) in self.angle_view_and_fix_obstruction:
            '''addition for each cam from the region cover taking fix obstruction in to account'''
            if camID in self.agent_id_taken_into_acount:
                coverage = coverage + res
        return coverage

    def find_distance_to_each_cam(self):
        """"
        :param
           - None

        :return
           - None

           This fills up the list self.distances, that cointaint the distance from every points from the mesh with respect to the cam
         """
        self.distances = []
        for agent in self.room.information_simulation.agentCams_list: #ici on se permet de prendre les cameras qui sont dans la description
            camera = agent.camera
            '''taking the position of the camera'''
            px, py = (camera.xc, camera.yc)
            x0 = px * np.ones(self.xv.shape)
            y0 = py * np.ones(self.yv.shape)

            ''' computting the distances, matrix computation !'''
            d = np.power(np.power((self.xv - x0), 2) + np.power((self.yv - y0), 2), 0.5)
            self.distances.append((camera.id, d))

    def find_angle_view_all_cam_and_fix_obstruction(self):
        """"
                       :param
                       - None

                       :return
                       - None

                       This fills up the list self.angle_view_and_obstruction (see description above)
               """
        self.angle_view_and_fix_obstruction = []
        for agent in self.room.information_simulation.agentCams_list:
            camera = agent.camera
            for item in self.angle_view:
                '''compute the region of vision from the cam, wihtout obstruction'''
                (camID, res) = item
                res = res.copy()
                if (camera.id == camID):
                    '''for every target in the room, suppress obstructed region from the res computed above'''
                    res = self.find_fix_obstruction(camera, res)
                    '''append the result for each cam'''
                    self.angle_view_and_fix_obstruction.append((camera.id, res))
                    break

    def find_angle_view_one_cam(self, cam):
        """"
        :param
            - cam : camera object we want to find the field of vision

        :return
            - fill the list self.angle_view (see description above)

        :com
            result = np.ones(self.xv.shape)*0 => camera see nothing
            -> 1 means point x, y is viewed
            -> 0 means point x, y is hidden
        """

        result = np.ones(self.xv.shape) * 0
        (i_tot, j_tot) = result.shape
        for i in range(i_tot):
            for j in range(j_tot):
                if is_x_y_radius_in_field_not_obstructed(cam,self.xv[i, j], self.yv[i, j]):
                    """"Turn the matrix to one when the camera sees the point (x,y)"""
                    result[i, j] = 1
        return result

    def find_angle_view_all_cam(self):
        """"
                        :param
                        -None

                        :return
                        - fill the list self.angle_view (see description above)

        """
        self.angle_view = []
        for agent in self.room.information_simulation.agentCams_list:
            camera = agent.camera
            res = self.find_angle_view_one_cam(camera)
            self.angle_view.append((camera.id, res))

    def find_fix_obstruction(self, cam, result):
        """"
        :param
            - cam : camera object we want to find the obstructed field of vision
            - result : mesh from the field of the camera. (Computed with find_angle of view)
                     a standart choice could be result = np.ones(self.xv.shape)
                      -> 1 means point x,y is viewed
                      -> 0 means point x,y is hidden
                       the function use the maps and turn 1 in 0 if the point is not in view.

        :return
            - a array from result's dimension. It gives the camera's field of vision with fix object in the room

           """
        return is_in_hidden_zone_fix_targets_matrix_x_y(self.room,cam.id,result, self.xv, self.yv)

