import constants
import matplotlib.pyplot as plt
from pylab import *
from my_utils.to_csv import *
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from mpl_toolkits.mplot3d import Axes3D

X_MIN = 0
X_MAX = 300
Y_MIN = 0
Y_MAX = 300
T_MIN = 0
T_MAX = 500


def plot_graph_3D(ax, x, y, z, title="title", x_label="x_axis", y_label="y_axis", z_label="z_label"):
    ax.plot(x, y, z, "x", label='parametric curve')

    # ax.set_xlim(0, max(x))
    # ax.set_ylim(0, max(y))
    ax.set_zlim(0, max(z))

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)

    ax.set_title(title)
    ax.legend()

    # Customize the z axis.
    # ax.zaxis.set_major_locator(LinearLocator(10))
    # ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))


def plot_graph_3D_2D(ax, x, y, z, size, title="title", x_label="x_axis", y_label="y_axis", curve_label="name here"):
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    my_norm = plt.Normalize(0, max(z))

    lc = LineCollection(segments, cmap='viridis', norm=my_norm)
    # Set the values used for colormapping
    lc.set_array(z)
    lc.set_linewidth(2)

    sc = ax.scatter(x, y, c=z, s=math.pow(size[0], 2) * math.pi)
    ax.plot(x, y, "x", label=curve_label)

    #   line = ax.add_collection(lc)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    ax.set_xlim(Y_MIN, X_MAX)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.grid(True)

    ax.legend()

    return sc


def plot_graph_2D(ax, x, y, title="title", x_label="x_axis", y_label="y_axis", curve_label="name here"):
    x = np.array(x)
    y = np.array(y)
    ax.plot(x, y, "x", label=curve_label)

    ax.grid(True)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)


def plot_graph_x_y(ax, x, y, title="title", x_label="x_axis", y_label="y_axis", curve_label="name here"):
    plot_graph_2D(ax, x, y, title=title, x_label=x_label, y_label=y_label, curve_label=curve_label)
    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(Y_MIN, Y_MAX)


def plot_graph_time_x(ax, time, x, title="title", x_label="x_axis", y_label="y_axis", curve_label="name here"):
    plot_graph_2D(ax, time, x, title=title, x_label=x_label, y_label=y_label, curve_label=curve_label)
    ax.set_xlim(T_MIN, T_MAX)


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
        self.simulated_data = load_csv_file_dictionnary("data_saved/simulated_data")
        self.data_sort_by_target = []
        self.simulated_data_sort_by_target = []

        self.sort_by_target(self.data, self.data_sort_by_target)
        self.sort_by_target(self.simulated_data, self.simulated_data_sort_by_target)

    def sort_by_target(self, list_init, list_sort):
        for data_element in list_init:
            is_in_list = False
            for element in list_sort:
                if data_element['target_signature'] == element.target_signature:
                    element.add_target_estimator(data_element, constants.TARGET_ESTIMATOR_CSV_FIELDNAMES)
                    is_in_list = True
                    break
            if not is_in_list:
                list_sort.append(
                    TargetSortedTargetEstimator(data_element['target_id'], data_element['target_signature'],
                                                constants.TARGET_ESTIMATOR_CSV_FIELDNAMES))

                list_sort[len(list_sort) - 1].add_target_estimator(data_element,
                                                                   constants.TARGET_ESTIMATOR_CSV_FIELDNAMES)

    def plot_all_target(self):
        self.plot_time_type_x_y_agent()

    def plot_a_target(self, target_id):
        self.plot_simulated_data_collected_data()

    def plot_simulated_data_collected_data(self):
        fig_time_type_x_y = plt.figure()
        ax1 = fig_time_type_x_y.add_subplot(2, 2, 1)
        ax2 = fig_time_type_x_y.add_subplot(2, 2, 2)
        ax3 = fig_time_type_x_y.add_subplot(2, 2, 3)
        ax4 = fig_time_type_x_y.add_subplot(2, 2, 4)

        for element in self.simulated_data_sort_by_target:
            sc1 = self.plot_target_memory_time_x_y_2D(ax1, element.data_list,
                                                      curve_label="target" + str(element.target_id))

        for element in self.data_sort_by_target:
            self.plot_target_memory_x_y(ax1, element.data_list, curve_label="target" + str(element.target_id))
            sc2 = self.plot_target_memory_type_x_y_2D(ax2, element.data_list,
                                                      curve_label="target" + str(element.target_id))
            sc3 = self.plot_target_memory_agent_x_y_2D(ax3, element.data_list,
                                                       curve_label="target" + str(element.target_id))
            self.plot_target_memory_time_agent(ax4, element.data_list, curve_label="target" + str(element.target_id))

        fig_time_type_x_y.colorbar(sc1, ax=ax1)
        fig_time_type_x_y.colorbar(sc2, ax=ax2)
        fig_time_type_x_y.colorbar(sc3, ax=ax3)

    def plot_time_type_x_y_agent(self, list):
        fig_time_type_x_y = plt.figure()
        ax1 = fig_time_type_x_y.add_subplot(2, 2, 1)
        ax2 = fig_time_type_x_y.add_subplot(2, 2, 2)
        ax3 = fig_time_type_x_y.add_subplot(2, 2, 3)
        ax4 = fig_time_type_x_y.add_subplot(2, 2, 4)

        for element in list:
            self.plot_target_memory_time_x_y_2D(ax1, element.data_list)
            self.plot_target_memory_type_x_y_2D(ax2, element.data_list)
            self.plot_target_memory_agent_x_y_2D(ax3, element.data_list)
            self.plot_target_memory_time_agent(ax4, element.data_list)

    def plot_time_type_x_y(self, list):
        fig_time_type_x_y = plt.figure()
        ax1 = fig_time_type_x_y.add_subplot(1, 2, 1)
        ax2 = fig_time_type_x_y.add_subplot(1, 2, 2)

        for element in list:
            self.plot_target_memory_time_x_y_2D(ax1, element.data_list)
            self.plot_target_memory_type_x_y_2D(ax2, element.data_list)

    def plot_type_x_y(self, list):
        fig_time_x_y_3D = plt.figure()
        fig_time_x_y_2D = plt.figure()
        fig_time_x_y = plt.figure()

        ax1 = fig_time_x_y.add_subplot(1, 2, 1, projection='3d')
        ax2 = fig_time_x_y.add_subplot(1, 2, 2)

        for element in list:
            self.plot_target_memory_type_x_y_2D(fig_time_x_y_2D.gca(), element.data_list)
            self.plot_target_memory_type_x_y_3D(fig_time_x_y_3D.gca(projection='3d'), element.data_list)

            self.plot_target_memory_type_x_y_2D(ax2, element.data_list)
            self.plot_target_memory_type_x_y_3D(ax1, element.data_list)

    def plot_time_x_y(self, list):
        fig_time_x_y_3D = plt.figure()
        fig_time_x_y_2D = plt.figure()
        fig_time_x_y = plt.figure()

        ax1 = fig_time_x_y.add_subplot(1, 2, 1, projection='3d')
        ax2 = fig_time_x_y.add_subplot(1, 2, 2)

        for element in list:
            self.plot_target_memory_time_x_y_2D(fig_time_x_y_2D.gca(), element.data_list)
            self.plot_target_memory_time_x_y_3D(fig_time_x_y_3D.gca(projection='3d'), element.data_list)

            self.plot_target_memory_time_x_y_2D(ax2, element.data_list)
            self.plot_target_memory_time_x_y_3D(ax1, element.data_list)

    def plot_time_agent(self, list):
        fig_time_type_x_y = plt.figure()
        ax1 = fig_time_type_x_y.add_subplot(1, 2, 1)
        ax2 = fig_time_type_x_y.add_subplot(1, 2, 2)

        for element in list:
            self.plot_target_memory_time_agent(ax1, element.data_list)
            self.plot_target_memory_time_agent(ax2, element.data_list)

    def plot_target_memory_type_x_y_2D(self, ax, data, curve_label):
        return plot_graph_3D_2D(ax, data[6], data[7], data[5], data[8], "x-y plane, type", "x []", "y []",
                                curve_label=curve_label)

    def plot_target_memory_type_x_y_3D(self, ax, data):
        plot_graph_3D(ax, data[6], data[7], data[5], "x-y plane, type", "x []", "y []")

    def plot_target_memory_time_x_y_2D(self, ax, data, curve_label="curve_label"):
        return plot_graph_3D_2D(ax, data[6], data[7], data[0], data[8], "x-y plane, time", "x []", "y []",
                                curve_label=curve_label)

    def plot_target_memory_time_x_y_3D(self, ax, data):
        plot_graph_3D(ax, data[6], data[7], data[0], "x-y plane, time", "x []", "y []")

    def plot_target_memory_agent_x_y_2D(self, ax, data, curve_label="curve_label"):
        return plot_graph_3D_2D(ax, data[6], data[7], data[1], data[8], "Agent generating info in terms of time",
                                "time []", "Agent [id]", curve_label=curve_label)

    def plot_target_memory_x_y(self, ax, data, curve_label="curve_label"):
        plot_graph_x_y(ax, data[6], data[7], "X in terms of time", "x []", "y []", curve_label=curve_label)

    def plot_target_memory_time_x(self, ax, data, curve_label="curve_label"):
        plot_graph_time_x(ax, data[0], data[6], "X in terms of time", "time []", "x []", curve_label=curve_label)

    def plot_target_memory_time_y(self, ax, data, curve_label="curve_label"):
        plot_graph_time_x(ax, data[0], data[7], "Y in terms of time", "time []", "y []", curve_label=curve_label)

    def plot_target_memory_time_agent(self, ax, data, curve_label="curve_label"):
        plot_graph_time_x(ax, data[0], data[1], "Agent generating info in terms of time", "time []", "Agent [id]",
                          curve_label=curve_label)


test = AnalyseMemoryAgent(100)
test.plot_a_target("0")
plt.show()
