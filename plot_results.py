import constants
import matplotlib.pyplot as plt
from pylab import *
from my_utils.to_csv import *
from mpl_toolkits.mplot3d import Axes3D


def plot_graph_3D(fig,x, y, z, title="title", x_label="x_axis", y_label="y_axis"):
    print("test")
    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    ax = fig.gca(projection='3d')
    ax.plot(x, y, z,"x", label='parametric curve')
    #ax.scatter(x, y, z, label='parametric curve')
    ax.legend()

    # Customize the z axis.
    #ax.set_zlim(-1.01, 1.01)
    #ax.zaxis.set_major_locator(LinearLocator(10))
    #ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

    # Add a color bar which maps values to colors.
    #fig.colorbar(surf, shrink=0.5, aspect=5)




def plot_graph_x_y(x, y, title="title", x_label="x_axis", y_label="y_axis"):
    plt.plot(x, y, "x")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.xlim(0, 300)
    plt.ylim(0, 300)
    plt.grid(True)
    plt.axis('equal')


def plot_graph_time_data(x, y, title="title", x_label="x_axis", y_label="y_axis"):
    plt.plot(x, y, "x")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)


class TargetSortedTargetEstimator:
    def __init__(self, taret_id, target_signature, fieldnames):
        self.target_id = taret_id
        self.target_signature = target_signature
        self.data_list = []
        self.init(fieldnames)

    def init(self, fieldnames):
        for i in range(len(constants.TARGET_ESTIMATOR_CSV_FIELDNAMES)):
            self.data_list.append([])

    def add_target_estimator(self, data, fieldnames):
        for i in range(len(constants.TARGET_ESTIMATOR_CSV_FIELDNAMES)):
            try:
                self.data_list[i].append(int(float(data[fieldnames[i]])))
            except ValueError:
                self.data_list[i].append(data[fieldnames[i]])


class AnalyseMemoryAgent:
    def __init__(self, agent_id):
        self.data = load_csv_file_dictionnary("data_saved/memory_agent/agent" + str(agent_id))
        self.data_sort_by_target = []

        for data_element in self.data:
            is_in_list = False
            for element in self.data_sort_by_target:
                if data_element['target_signature'] == element.target_signature:
                    element.add_target_estimator(data_element, constants.TARGET_ESTIMATOR_CSV_FIELDNAMES)
                    is_in_list = True
                    break
            if not is_in_list:
                self.data_sort_by_target.append(
                    TargetSortedTargetEstimator(data_element['target_id'], data_element['target_signature'],
                                                constants.TARGET_ESTIMATOR_CSV_FIELDNAMES))

                self.data_sort_by_target[len(self.data_sort_by_target) - 1].add_target_estimator(data_element,
                                                                                                 constants.TARGET_ESTIMATOR_CSV_FIELDNAMES)

    def plot_all_target(self):
        fig = plt.figure()
        for element in self.data_sort_by_target:
            # self.plot_target_memory_x_y(element.data_list)
            #self.plot_target_memory_time_type(element.data_list)
            self.plot_test(fig,element.data_list)

    def plot_a_target(self, target_id):
        for element in self.data_sort_by_target:
            if element.target_id == target_id:
                # self.plot_target_memory_x_y(element.data_list)
                self.plot_test(element.data_list)

    def plot_test(self,fig,data):
        plot_graph_3D(fig,data[6], data[7], data[0])

    def plot_target_memory_time_x(self, data):
        plot_graph_time_data(data[0], data[6], "X in terms of time", "time []", "x []")

    def plot_target_memory_time_y(self, data):
        plot_graph_time_data(data[0], data[7], "Y in terms of time", "time []", "y []")

    def plot_target_memory_x_y(self, data):
        plot_graph_x_y(data[6], data[7], "x-y plane", "x []", "y []")

    def plot_target_memory_time_id_agent(self, data):
        plot_graph_time_data(data[0], data[1], "x-y plane", "x []", "y []")

    def plot_target_memory_time_type(self, data):
        plot_graph_time_data(data[0], data[5], "x-y plane", "x []", "y []")


test = AnalyseMemoryAgent(100)
test.plot_all_target()
plt.show()