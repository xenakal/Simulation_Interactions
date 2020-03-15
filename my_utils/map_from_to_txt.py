import re
import math
import main
from elements import room

"""
        Class use to save and load room
"""
class Room_txt():

    def __init__(self):
        """
            Data to save contains all the data to reconstruct the room
        """
        self.x_target = []
        self.y_target = []
        self.vx_target = []
        self.vy_target = []
        self.trajectoire_target = []
        self.trajectoire_choice = []
        self.label_target = []
        self.size_target = []
        self.t_add = []
        self.t_del = []

        self.x_cam = []
        self.y_cam = []
        self.alpha_cam = []
        self.beta_cam = []
        self.fix = []

        self.traj_all = []
        self.traj = []

        self.data_to_save = []
        self.actualise_data_to_save()


    def save_room_to_txt(self):
        fichier = open(main.PATH_TO_SAVE_MAP+main.SAVE_MAP_NAME, "w")
        fichier.write("# New Map, but you can change the name \n")
        fichier.write("# Please let the blank where they are, \n")
        fichier.write("# Otherwise the map will not be loaded correctly. \n")
        fichier.write("# This save is not dummysproof \n")
        fichier.write("#---------------------------- \n")
        fichier.write("# 10 lines to save target data \n")
        fichier.write("# 5 lines to save target data \n")
        fichier.write("# Description start below this line \n")
        fichier.write("#==================================\n")
        fichier.write("#\n")
        count = 0
        for element in self.data_to_save:
            if count == 0:
                fichier.write("#Targets description \n")
                fichier.write("#---------------------------- \n")
            if count == 10:
                fichier.write("#Cameras description \n")
                fichier.write("#---------------------------- \n")
            if count == 15:
                fichier.write("#Trajectories description \n")
                fichier.write("#---------------------------- \n")

            fichier.write("*")
            for each in element:
                fichier.write(str(each) + str(","))

            fichier.write("\n")
            count = count + 1
        fichier.write("#---------------------------- \n")
        fichier.write("#end of file \n")
        fichier.close()

    def load_room_from_txt(self,fileName = 0):
        if fileName == 0:
            fileName =  main.LOAD_MAP_NAME

        fichier = open(main.PATH_TO_LOAD_MAP+fileName,"r")
        lines = fichier.readlines()
        fichier.close()

        self.clean()
        count = 0
        for line in lines:

           if not (line[0] == "#"):
                line = line[1:]

                if(count == 8):
                    self.t_add = self.from_listString_to_list(line)
                    self.data_to_save[8] = self.t_add
                elif (count == 9):
                    self.t_del = self.from_listString_to_list(line)
                    self.data_to_save[9] = self.t_del
                elif (count == 15):
                    self.traj_all = self.from_trajString_to_traj(line)
                    self.data_to_save[15] = self.traj_all

                else:
                    linesplit = re.split(",",line)
                    for  elem in linesplit:
                        if not(elem == "\n"):
                            try:
                                self.data_to_save[count].append(math.ceil(float(elem)))
                            except ValueError:
                                self.data_to_save[count].append(elem)
                count = count + 1

        self.from_all_data_to_separate()

    def from_trajString_to_traj(self,s):
        list = []
        traj = re.split("]\),",s)
        for item in traj:
            try:
                num_traj_split = re.split(", \[\(",item)
                sublist = []
                num  =  num_traj_split[0][1:]
                traj_num = num_traj_split[1][0:len(num_traj_split[1])-1]
                numbers = re.split("\), \(",traj_num)
                for number in numbers:
                    xy = re.split(", ",number)
                    sublist.append((int(xy[0]),int(xy[1])))
                list.append((int(num), sublist))
            except IndexError:
                pass
        return list

    def from_listString_to_list(self,s):
        list = []
        if not(s == ""):
            s = re.split("],",s)
            for item in s:
                sublist = []

                item = item[1:len(item)]
                numbers = re.split(",", item)
                for number in numbers:
                    if not (number == ""):
                        try:
                            sublist.append(int(number))
                        except IndexError:
                            pass
                if not (item == ""):
                    list.append(sublist)
        return list


    def init_room(self):
        my_room = room.Room()
        '''Frist to give the trajectories cause needed to create the target'''
        my_room.init_trajectories(self.traj_all)
        '''Create the taget'''
        my_room.init_room(self.x_target, self.y_target, self.vx_target, self.vy_target, self.trajectoire_target,
                              self.trajectoire_choice, self.label_target, self.size_target, self.t_add, self.t_del)
        '''Create the agent'''
        my_room.init_agentCam(self.x_cam, self.y_cam, self.alpha_cam, self.beta_cam, self.fix,my_room)

        return my_room

    def from_room_to_seprarate(self,room):
        self.clean()
        self.my_new_room = room

        for target in self.my_new_room.info_simu.targets_SIMU:
            self.add_target(target.xc,target.yc,target.vx,target.vy,target.trajectory,target.trajectory_choice,
                            target.label,target.size,target.t_add,target.t_del)

        for agent in self.my_new_room.agentCams:
            camera = agent.cam
            '''need to go from radian to degree'''
            self.add_cam(camera.xc,camera.yc,camera.alpha*180/math.pi,camera.beta*180/math.pi,camera.fix)
        self.actualise_data_to_save()

    def add_point_traj(self,x,y):
        self.traj.append((x,y))

    def del_point_traj(self,x,y):
        try :
            self.traj.remove((x,y))
        except ValueError:
            pass

    def clean_traj(self):
        self.traj = []

    def add_traj_to_all_traj(self):
        count = 0
        for item in self.traj_all:
            count = count + 1
        self.traj_all.append((count,self.traj))

    def set_traj_to_all_traj(self,n):
        for item in self.traj_all:
            (num,my_traj) = item
            if n == num:
               return my_traj
        return []

    def rem_traj_to_all_traj(self,n):
        for item in self.traj_all:
            (num,my_traj) = item
            if n == num:
                try:
                    self.traj_all.remove((num,my_traj))
                    break
                except ValueError:
                    pass

    def add_target(self,x,y,vx,vy,traj_label,traj_choice, label,size,t_add,t_del):
        self.x_target.append(x)
        self.y_target.append(y)
        self.vx_target.append(vx)
        self.vy_target.append(vy)
        self.trajectoire_target.append(traj_label)
        self.trajectoire_choice.append(traj_choice)
        self.label_target.append(label)
        self.size_target.append(size)
        self.t_add.append(t_add)
        self.t_del.append(t_del)

    def add_cam(self,x,y,alpha,beta,fix):
        self.x_cam.append(x)
        self.y_cam.append(y)
        self.alpha_cam.append(alpha)
        self.beta_cam.append(beta)
        self.fix.append(fix)

    def clean(self):
        self.my_new_room = room.Room()

        self.x_target = []
        self.y_target = []
        self.vx_target = []
        self.vy_target = []
        self.trajectoire_target = []
        self.trajectoire_choice = []
        self.label_target = []
        self.size_target = []
        self.t_add = []
        self.t_del = []

        self.x_cam = []
        self.y_cam = []
        self.alpha_cam = []
        self.beta_cam = []
        self.fix = []

        self.traj = []
        self.traj_all = []
        self.actualise_data_to_save()

    def actualise_data_to_save(self):
        self.data_to_save = [self.x_target, self.y_target, self.vx_target, self.vy_target, self.trajectoire_target,
                             self.trajectoire_choice, self.label_target,
                             self.size_target, self.t_add, self.t_del, self.x_cam, self.y_cam, self.alpha_cam,
                             self.beta_cam, self.fix,self.traj_all]

    def from_all_data_to_separate(self):
        self.x_target = self.data_to_save[0]
        self.y_target = self.data_to_save[1]
        self.vx_target = self.data_to_save[2]
        self.vy_target = self.data_to_save[3]
        self.trajectoire_target = self.data_to_save[4]
        self.trajectoire_choice = self.data_to_save[5]
        self.label_target = self.data_to_save[6]
        self.size_target = self.data_to_save[7]
        self.t_add = self.data_to_save[8]
        self.t_del = self.data_to_save[9]

        self.x_cam = self.data_to_save[10]
        self.y_cam = self.data_to_save[11]
        self.alpha_cam = self.data_to_save[12]
        self.beta_cam = self.data_to_save[13]
        self.fix = self.data_to_save[14]

        self.traj_all = self.data_to_save[15]