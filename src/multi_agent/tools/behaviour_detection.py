import numpy as np
import src.multi_agent.elements.camera as aCam


class TargetBehaviourAnalyser:
    """
        Class TargetBehaviourAnalyser.

        Description : Class to get information on the behaviour of a target in order to help taking descision

            :params
                1. (FusionList) room_memory -- description of every target for all times in the room

            :attibutes
                1. (type) name -- description

            :notes
                fells free to write some comments.
    """

    def __init__(self, memory):
        self.room_memory = memory.memory_use_to_send_information_from_target

    def is_target_stopped(self, target_id, delta_t, n, thresh):
        """
                    :description
                        based on multiple position, we want to detect if the target was moving and stops
                    :params

                        1.(int) targetID     -- target identification number
                        2.(int) deltaT > 0   -- how many times we wants to check back
                        3.(int) n > 3        -- number of previous position to take into account
                        4.(int) thresh       -- thresh, must be a little bit higher than the noise level
                                                (for the actual settings 3 is a good value)

                    :return / modify vector
                        1. (boolean) is_stopped -- true if the target does not move on the deltaT periode

                    :note
                        see self.detect_target_motion(targetID, deltaT, n, thresh)
                """
        (is_moving, is_stopped) = self.detect_target_motion(target_id, delta_t, n, thresh)
        return is_stopped

    def is_target_moving(self, target_id, delta_t, n, thresh):
        """
                    :description
                        based on multiple position, we want to detect if the target was moving and stops
                    :params

                        1.(int) targetID     -- target identification number
                        2.(int) deltaT > 0   -- how many times we wants to check back
                        3.(int) n > 3        -- number of previous position to take into account
                        4.(int) thresh       -- thresh, must be a little bit higher than the noise level
                                                (for the actual settings 3 is a good value)

                    :return / modify vector
                        1. (boolean) is_moving -- true if the target is moving on the deltaT periode

                    :note
                        see self.detect_target_motion(targetID, deltaT, n, thresh)
                """
        (is_moving, is_stopped) = self.detect_target_motion(target_id, delta_t, n, thresh)
        return is_moving

    def is_target_changing_state(self, target_id, delta_t, n, thresh):
        """
                    :description
                        based on multiple position, we want to detect if the target was moving and stops
                    :params

                        1.(int) targetID     -- target identification number
                        2.(int) deltaT > 0   -- how many times we wants to check back
                        3.(int) n > 3        -- number of previous position to take into account
                        4.(int) thresh       -- thresh, must be a little bit higher than the noise level7
                                                (for the actual settings 3 is a good value)

                    :return / modify vector
                        1. (boolean) is_changing_state -- true if the target is moving and is stopped on the given period

                    :note
                        see self.detect_target_motion(targetID, deltaT, n, thresh)
                """
        (is_moving, is_stopped) = self.detect_target_motion(target_id, delta_t, n, thresh)
        return is_moving and is_stopped

    def detect_target_motion(self, target_id, delta_t, n, thresh):
        """
             :description
                 based on multiple position, we want to detect if the target was moving and stops
             :params

                 1.(int) targetID     -- target identification number
                 2.(int) deltaT > 0   -- how many times we wants to check back
                 3.(int) n > 3        -- number of previous position to take into account
                 4.(int) thresh       -- thresh, must be a little bit higher than the noise level
                                        (for the actual settings 3 is a good value)

             :return / modify vector
                 1. (boolean) (is_moving,is_stopped) --

                    is_moving | is_stopped
                    -----------------------
                    False     | False       -> Error cause not enough data to compute
                    True      | False       -> Target is moving
                    False     | True        -> Target is stopped
                    True      | True        -> Target is both, so changed state in the deltaT time

                 if the two args are false, then there is not enough mesures to IO_data.py the data

            :note
                1.(boolean list) state -- True if the target is stopped for the time t - deltaT(i)
         """
        list_to_check = self.room_memory.get_item_list(target_id)
        list_len = len(list_to_check)

        state = []
        test_stopped = []
        test_mooving = []
        is_moving = False
        is_stopped = False

        if n + delta_t < list_len:
            for time in range(delta_t):
                state.append(self.is_target_fix(target_id, time, n, thresh))
                test_stopped.append(True)
                test_mooving.append(False)

            if state == test_stopped:
                is_stopped = True
            elif state == test_mooving:
                is_moving = True
            elif not is_moving and not is_stopped:
                is_moving = True
                is_stopped = True

        return is_moving, is_stopped

    def is_target_fix(self, target_id, t, n, thresh):
        """
            :description
                based on multiple position, we want to detect if the target is fix
            :params
                1.(int) targetID  -- target identification number
                2.(int) t >= 0    -- to check t times before the actuall time in the simulation
                3.(int) n > 3     -- number of previous position to take into account
                4.(int) thresh    -- thresh, must be a little bit higher than the noise level
                                     (for the actual settings 3 is a good value)

            :return / modify vector
                1. (boolean) fix -- true if the target seems to be stationary otherwise false
        """

        list_to_check = self.room_memory.get_item_list(target_id)
        list_len = len(list_to_check)
        if n <= list_len:
            list_to_check = list_to_check[list_len - n - t:list_len - t]

            x = []
            y = []
            for item in list_to_check:
                x.append(item.item_position[0])
                y.append(item.item_position[1])

            x_sdt = np.std(x)
            y_sdt = np.std(y)

            if x_sdt < thresh and y_sdt < thresh:
                return True
        return False

    def is_target_leaving_cam_field(self, camera, targetID, t, n):
        """
            :description
                based on multiple position, we want to detect if the target is leaving the camera field

            :params
                1.(Camera) cam    -- camera object
                2.(int) targetID  -- target identification number
                3.(int) t >= 0    -- to check t times before the actuall time in the simulation
                4.(int) n > 3     -- number of previous position to take into account

            :return / modify vector
                1. (boolean) (is_in_field,is_out_field) --

                    is_in_field | is_out_field
                    -----------------------
                      False     |   False       -> Error cause not enough data to compute
                      True      |   False       -> Target is in the field
                      False     |   True        -> Target is outside
                      True      |   True        -> Target is both, so changed state in the n measure

            :note
            ! Attention !
            This method should be use with prediction or data received from other cams.
            In fact the camera is not able to give data outside from its range
        """

        list_to_check = self.room_memory.get_item_list(targetID)
        field = []
        in_field = []
        out_field = []

        is_in_field = False
        is_out_field = False

        list_len = len(list_to_check)
        if n <= list_len:
            list_to_check = list_to_check[list_len - n - t:list_len - t]

            for item in list_to_check:
                field.append(
                    aCam.is_x_y_radius_in_field_not_obstructed(camera, item.item_position[0], item.item_position[1]))
                in_field.append(True)
                out_field.append(False)

            if field == in_field:
                is_in_field = True
            elif field == out_field:
                is_out_field = True
            elif not is_in_field and not is_out_field:
                is_in_field = True
                is_out_field = True

        return (is_in_field, is_out_field)
