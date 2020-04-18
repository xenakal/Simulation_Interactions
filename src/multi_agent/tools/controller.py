import math
import numpy as np
class ControllerP:
    def __init__(self, value_target, kp):
        self.kp = kp
        self.value_target = value_target
        self.error = 0
        self.command_max = 1

    def born_command(self, command):
        if math.fabs(command) > self.command_max:
            return np.sign(command) * self.command_max
        else:
            return command

    def get_command(self, value):
        self.error = self.value_target - value
        command = self.kp * self.error
        command = self.born_command(command)
        return command


class ControllerPI(ControllerP):
    def __init__(self, value_target, kp, ki):
        super().__init__(value_target, kp)
        self.ki = ki
        self.sum_error = 0

    def reset(self):
        self.sum_error = 0

    def get_command(self, value):
        self.error = self.value_target - value
        self.sum_error += self.error
        command = self.kp * self.error + self.ki * self.sum_error
        command = self.born_command(command)
        return command


class CameraController:
    def __init__(self,kp_pos,ki_pos,kp_alpha,ki_alpha,kp_beta,ki_beta):
        self.position_controller = PositionController(0,0,kp_pos,ki_pos)
        self.alpha_controller = OrientationController(0,kp_alpha,ki_alpha)
        self.beta_controller = ZoomController(0, kp_beta, ki_beta)

    def set_targets(self,x_target,y_target,alpha_target,beta_target):
        self.set_post_target(x_target,y_target)
        self.set_alpha_target(alpha_target)
        self.set_beta_target(beta_target)

    def set_targets_based_on_config(self, configuration):
        self.set_post_target(configuration.x, configuration.y)
        self.set_alpha_target(configuration.alpha)
        self.set_beta_target(configuration.beta)

    def set_post_target(self,x_target,y_target):
        self.position_controller.x_controller.value_target = x_target
        self.position_controller.y_controller.value_target = y_target

    def set_alpha_target(self,alpha_target):
        self.alpha_controller.value_target = self.alpha_controller.bound_alpha_btw_minus_pi_plus_pi(alpha_target)

    def set_beta_target(self,beta_target):
        self.beta_controller.value_target = beta_target

    def get_command(self,x_mes,y_mes,alpha_mes,beta_mes):
        x_command,y_command = self.get_pos_command(x_mes,y_mes)
        return x_command,y_command, self.get_alpha_command(alpha_mes), self.get_beta_command(beta_mes)

    def get_pos_command(self, x_mes, y_mes):
        return self.position_controller.get_command(x_mes,y_mes)

    def get_alpha_command(self,alpha_mes):
        return self.alpha_controller.get_command(alpha_mes)

    def get_beta_command(self,beta_mes):
        return self.beta_controller.get_command(beta_mes)

class PositionController:
    def __init__(self, x_target, y_target, kp, ki):
        self.x_controller = ControllerPI(x_target, kp, ki)
        self.y_controller = ControllerPI(y_target, kp, ki)

    def get_command(self, x_mes, y_mes):
        x_command = self.x_controller.get_command(x_mes)
        y_command = self.y_controller.get_command(y_mes)
        return x_command, y_command


class OrientationController(ControllerPI):
    def __init__(self, alpha_target, kp, ki):
        alpha_target = self.bound_alpha_btw_minus_pi_plus_pi(alpha_target)
        super().__init__(alpha_target, kp, ki)

    def bound_alpha_btw_minus_pi_plus_pi(self,angle):
        if math.fabs(angle) > math.pi:
            return -np.sign(angle)*(math.pi - np.sign(angle)*math.fmod(angle,math.pi))

        return angle

    def get_command(self, value):
        value = self.bound_alpha_btw_minus_pi_plus_pi(value)

        self.error = self.value_target - value
        if math.fabs(self.error) < 0.001:
            return 0

        if self.error > 2*math.pi:
            print("oupsi error get_command orientationController")
        elif math.fabs(self.error) > math.pi:
            self.error = -np.sign(self.error)*(2*math.pi- math.fabs(self.error))

        self.sum_error += self.error
        command = self.kp * self.error + self.ki * self.sum_error
        command = self.born_command(command)
        return command

class ZoomController((ControllerPI)):
    def __init__(self, beta_target, kp, ki):
        super().__init__(beta_target, kp, ki)


