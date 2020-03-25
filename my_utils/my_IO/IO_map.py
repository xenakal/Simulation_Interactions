import re
import math
from multi_agent.elements import room
import constants
from multi_agent.elements.target import Target
from multi_agent.elements.camera import Camera
from multi_agent.agent.agent_interacting_room_camera import AgentCam
from multi_agent.agent.agent_interacting_room_user import AgentUser

"""
        Class use to save and load room
"""


def save_target_txt(fichier, room):
    for target in room.information_simulation.Target_list:
        fichier.write("target: " + target.save_target_to_txt())
        target.load_from_txt(target.save_target_to_txt())


def save_agent_cam(fichier, room):
    for agent in room.agentCams_list:
        fichier.write("camera: " + agent.camera.save_target_to_txt()[:-1] + " agent: " + agent.save_agent_to_txt())


def save_room_to_txt(filename, room):
    fichier = open(constants.PATH_TO_SAVE_MAP + filename, "w")
    fichier.write("New Map, but you can change the name \n \n")
    fichier.write("This file is the representation to initialise a room description \n")
    fichier.write("__________________________________________________________________ \n\n")
    fichier.write("!! You can modify the file, but pay attention to spaces and sign such as , -  !! \n")
    fichier.write("\n")
    save_target_txt(fichier, room)
    save_agent_cam(fichier, room)


def load_target_txt(s, room):
    target = Target()
    target.load_from_txt(s)
    room.add_Target(target)


def load_agentCam_txt(s, room):
    s = s.replace("\n", "")
    s = s.replace(" ", "")
    camera_agent = re.split("camera:|agent:", s)

    camera = Camera(room, -1, -1, -1, -1, -1)
    camera.load_from_txt(camera_agent[1])
    agent = AgentCam(camera)
    agent.load_from_txt(camera_agent[2])
    room.add_AgentCam(agent)


def load_room_from_txt(filename, room):
    fichier = open(constants.PATH_TO_LOAD_MAP + filename, "r")
    lines = fichier.readlines()
    fichier.close()

    for line in lines:
        if "target:" in line:
            load_target_txt(line[8:], room)
        if "camera:" in line:
            load_agentCam_txt(line, room)
