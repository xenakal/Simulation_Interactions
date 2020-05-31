from src import constants
from src.my_utils.my_IO.IO_data import load_csv_file_dictionnary
import matplotlib.pyplot as plt
from src.plot_functions.plot_toolbox import plot_graph_3D_2D, T_MIN, T_MAX, plot_graph_time_x
import numpy as np

TIME_TO_COMPARE = 0
TIME_INDEX = 1
AGENT_INDEX = 2
TYPE_INDEX = 6
X_INDEX = 7
Y_INDEX = 8
VX_INDEX = 9
VY_INDEX = 10
AX_INDEX = 11
AY_INDEX = 12
ALPHA_INDEX = 13



def plot_target_memory_time_x_y_2D(ax, data, curve_label="curve_label"):
    return plot_graph_3D_2D(ax, data[X_INDEX], data[Y_INDEX], data[TIME_INDEX], [0.2], T_MIN, T_MAX,
                            "Trajectory x-y plane  (time [s] in color)", "x [m]", "y [m]",curve_label=curve_label)

def plot_agent_time_alpha(ax, data, curve_label="curve_label"):
    plot_graph_time_x(ax, data[TIME_INDEX], np.degrees(data[ALPHA_INDEX]), "alpha in terms of time", "time [s]", "x [m]",
                      curve_label=curve_label)

def init_analyse_memory_agent(list_init, list_sort):
    for data_element in list_init:
        is_in_list = False

        for element in list_sort:
            if int(data_element['agent_id']) == int(element.agent_id):
                element.add_agent_estimator(data_element)
                is_in_list = True
                break

        if not is_in_list:
            "Create a new TargetSortedTargetEstimator"
            agent_created = AgentSortedAgentEstimator(int(data_element['agent_id']))
            "Add Data"
            agent_created.add_agent_estimator(data_element)
            list_sort.append(agent_created)

    list_sort.sort()

def loadfile(agent_id):
    sorted_list = []
    init_analyse_memory_agent(load_csv_file_dictionnary(constants.ResultsPath.SAVE_LOAD_DATA_AGENT_ESTIMATOR + str(agent_id)), sorted_list)
    return sorted_list

def plot(data,id):
        fig = plt.figure(figsize=(12, 8))
        fig.suptitle('Agent estimator', fontsize=17, fontweight='bold', y=0.98)
        fig.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
        ax1 = fig.add_subplot(1, 2, 1)
        ax2 = fig.add_subplot(1, 2, 2)

        for element in data:
            sc1 = plot_target_memory_time_x_y_2D(ax1, element.data_list,curve_label="agent"+str(element.agent_id))
            plot_agent_time_alpha(ax2,element.data_list,curve_label="agent"+str(element.agent_id))

        fig.colorbar(sc1, ax=ax1)

        fig.savefig(constants.ResultsPath.PLOT_AGENT_ESTIMATOR+"/agent_" + str(id))


class AgentSortedAgentEstimator:
    def __init__(self, agent_id):
        self.agent_id = int(agent_id)
        self.data_list = []
        self.init()

    def init(self):
        for i in range(len(constants.AGENT_ESTIMATOR_CSV_FIELDNAMES)):
            self.data_list.append([])

    def add_agent_estimator(self, data):
        for i in range(len(constants.AGENT_ESTIMATOR_CSV_FIELDNAMES)):
            try:
                self.data_list[i].append(float(data[constants.AGENT_ESTIMATOR_CSV_FIELDNAMES[i]]))
            except:
                self.data_list[i].append(data[constants.AGENT_ESTIMATOR_CSV_FIELDNAMES[i]])


    def __eq__(self, other):
        return self.agent_id == other.agent_id

    def __lt__(self, other):
        return self.agent_id < other.agent_id

    def __gt__(self, other):
        return self.agent_id > other.agent_id


class AgentEstimatorPloter:
    def __init__(self,agent_id):
        self.agent_id = agent_id
        self.data = loadfile(agent_id)

    def plot(self):
        plot(self.data,self.agent_id)




if __name__ == '__main__':
    constants.ResultsPath.folder = "../../results"
    constants.ResultsPath.name_simulation = "test1"
    agent_ploter = AgentEstimatorPloter(1)
    agent_ploter.plot()

