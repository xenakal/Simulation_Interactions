from code.multi_agent.tools.map_region_static import*


class MapRegionDynamic(MapRegionStatic):
    """
                Class use to detect the derministic region of action from different cameras

                :param
                - room, an object Room that describe the room itself
                - factor, room discretation from 1 to infinite. The bigger the number, the faster the computation will be (less precision).
    """

    def __init__(self, room):
        super().__init__(room)
        self.angle_view_and_obstruction = []

    def compute(self,label):
        self.minimum_id_in_view = np.ones(self.xv.shape) * 1000000000
        self.minimum_dist_in_view = np.ones(self.xv.shape) * 1000000000
        self.id_in_view = np.ones(self.xv.shape) * 1000000000
        self.coverage = np.ones(self.xv.shape) * 1000000000

        self.update_active_cams()
        '''Required for the computation below'''
        if label == "all":
            self.find_angle_view_and_obstruction()
        elif label =="small":
            self.find_angle_view_and_obstruction_small_region()

        '''Computation'''
        (self.minimum_id_in_view, self.minimum_dist_in_view) = self.define_region_covered_by_cams()
        self.coverage = self.define_region_covered_by_numberOfCams()

    def compute_all_map(self,factor = 3):
        (self.xv,self.yv) = create_region(self.nx,self.ny,factor)
        self.compute("all")

    def compute_small_region(self,x,y,x_offset,y_offset,factor=1):
        (self.xv, self.yv) = create_region(x,y,factor,x_offset,y_offset)
        self.compute("small")

    def define_region_covered_by_cams(self):
        """
                   :param
                   - None

                   :return (minimum_id_in_view, minimum_dist_in_view,id_in_view)
                   - minimum_id_in_view = give the id of the cam in charge for the point x,y from the grid
                   - minimum_dist_in_view = give the closest distance to a cam for the point x,y from the grid
                   - id_in_view = all the cam that can see the point x,y (! NOT WORKING YET)
               """
        '''Initialisation'''
        minimum_dist_in_view = np.ones(self.xv.shape) * 1000000000
        minimum_id_in_view = np.ones(self.xv.shape) * -1
        result = np.ones(self.xv.shape) * -1
        (i_tot, j_tot) = result.shape

        '''Computation for every cam, we need to check every distance'''
        for (camID, res) in self.angle_view_and_obstruction:
            for (camID_dist, distance) in self.distances:
                if (camID == camID_dist) and  camID in self.agent_id_taken_into_acount:
                    res_int = (res == 1)  # In the visible region
                    '''Check the all array res_int'''
                    for i in range(i_tot):
                        for j in range(j_tot):
                            if res_int[i, j]:
                                'add the point in the list of the camID'
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
        coverage = np.ones(self.xv.shape)*0

        for (camID,res) in self.angle_view_and_obstruction:
            '''addition for each cam from the region cover taking fix obstruction in to account'''
            if camID in self.agent_id_taken_into_acount:
                coverage = coverage + res
        return coverage

    def find_angle_view_and_obstruction(self):
        """"
                :param
                - None

                :return
                - None

                This fills up the list self.angle_view_and_obstruction (see description above)
        """
        self.angle_view_and_obstruction = []
        for agent in self.room.active_AgentCams_list:
            camera = agent.camera
            for item in self.angle_view_and_fix_obstruction:
                '''compute the region of vision from the cam, wihtout obstruction'''
                (camID,res) = item
                res = res.copy()
                if camera.id==camID:
                    '''for every target in the room, suppress obstructed region from the res computed above'''
                    res = self.find_dynamic_obstruction(camera,res)
                    '''append the result for each cam'''
                    self.angle_view_and_obstruction.append((camera.id,res))
                    break


    def find_angle_view_and_obstruction_small_region(self):
        """"
                :param
                - None

                :return
                - None

                This fills up the list self.angle_view_and_obstruction (see description above)
        """
        self.angle_view_and_obstruction = []
        for agent in self.room.active_AgentCams_list:
            '''compute the region of vision from the cam, wihtout obstruction'''
            res = self.find_angle_view_one_cam(agent.cam)
            '''for every target in the room, suppress obstructed region from the res computed above'''
            res = self.find_fix_obstruction(agent.cam, res)
            '''append the result for each cam'''
            self.angle_view_and_obstruction.append((agent.cam.id, res))

    def find_dynamic_obstruction(self,cam,result):
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
        return cam.is_in_hidden_zone_mooving_targets_matrix_x_y(result, self.xv, self.yv)

    def find_obstruction(self,cam,result):
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
        return cam.is_in_hidden_zone_all_targets_matrix_x_y(result, self.xv, self.yv)


