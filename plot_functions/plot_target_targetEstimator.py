from plot_functions.plot_toolbox import *

PATH_LOAD_DATA = "data_saved/data/memory_agent/agent"
PATH_LOAD_DATA_REF = "data_saved/data/simulated_data"
PATH_SAVE_PLOT = "data_saved/plot/plot_memory_agent/"

#PATH_LOAD_DATA = "../data_saved/data/memory_agent/agent"
#PATH_LOAD_DATA_REF = "../data_saved/data/simulated_data"
#PATH_SAVE_PLOT = "../data_saved/plot/plot_memory_agent/"
VERSION_SAVE_PLOT = "test-"


def sort_by_target(list_init, list_sort):
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
    list_sort.sort()


def plot_target_memory_type_x_y_2D(ax, data, curve_label):
    return plot_graph_3D_2D(ax, data[6], data[7], data[5], data[8], 0, 4, "x-y plane, type", "x []", "y []",
                            curve_label=curve_label)


def plot_target_memory_time_x_y_2D(ax, data, curve_label="curve_label"):
    return plot_graph_3D_2D(ax, data[6], data[7], data[0], data[8], T_MIN, T_MAX, "x-y plane, time", "x []", "y []",
                            curve_label=curve_label)


def plot_target_memory_agent_x_y_2D(ax, data, curve_label="curve_label"):
    return plot_graph_3D_2D(ax, data[6], data[7], data[1], data[8], 0, 2, "x-y plane agent",
                            "x []", "y []", curve_label=curve_label)


def plot_target_memory_x_y(ax, data, curve_label="curve_label"):
    plot_graph_x_y(ax, data[6], data[7], "x-y plane, time", "x []", "y []", curve_label=curve_label)


def plot_target_memory_time_x(ax, data, curve_label="curve_label"):
    plot_graph_time_x(ax, data[0], data[6], "X in terms of time", "time []", "x []", curve_label=curve_label)


def plot_target_memory_type_x_y_3D(ax, data):
    plot_graph_3D(ax, data[6], data[7], data[5], "x-y plane, type", "x []", "y []")


def plot_target_memory_time_x_y_3D(ax, data):
    plot_graph_3D(ax, data[6], data[7], data[0], "x-y plane, time", "x []", "y []")


def plot_target_memory_time_y(ax, data, curve_label="curve_label"):
    plot_graph_time_x(ax, data[0], data[7], "Y in terms of time", "time []", "y []", curve_label=curve_label)


def plot_target_memory_time_agent(ax, data, curve_label="curve_label"):
    plot_graph_time_x(ax, data[0], data[1], "Agent generating info in terms of time", "time []", "Agent [id]",
                      curve_label=curve_label)


def plot_time_type_x_y_agent(list):
    fig_time_type_x_y = plt.figure()
    ax1 = fig_time_type_x_y.add_subplot(2, 2, 1)
    ax2 = fig_time_type_x_y.add_subplot(2, 2, 2)
    ax3 = fig_time_type_x_y.add_subplot(2, 2, 3)
    ax4 = fig_time_type_x_y.add_subplot(2, 2, 4)
    for element in list:
        plot_target_memory_time_x_y_2D(ax1, element.data_list)
        plot_target_memory_type_x_y_2D(ax2, element.data_list)
        plot_target_memory_agent_x_y_2D(ax3, element.data_list)
        plot_target_memory_time_agent(ax4, element.data_list)


def plot_time_type_x_y(list):
    fig_time_type_x_y = plt.figure()
    ax1 = fig_time_type_x_y.add_subplot(1, 2, 1)
    ax2 = fig_time_type_x_y.add_subplot(1, 2, 2)
    for element in list:
        plot_target_memory_time_x_y_2D(ax1, element.data_list)
        plot_target_memory_type_x_y_2D(ax2, element.data_list)


def plot_time_x_y(list):
    fig_time_x_y_3D = plt.figure()
    fig_time_x_y_2D = plt.figure()
    fig_time_x_y = plt.figure()
    ax1 = fig_time_x_y.add_subplot(1, 2, 1, projection='3d')
    ax2 = fig_time_x_y.add_subplot(1, 2, 2)
    for element in list:
        plot_target_memory_time_x_y_2D(fig_time_x_y_2D.gca(), element.data_list)
        plot_target_memory_time_x_y_3D(fig_time_x_y_3D.gca(projection='3d'), element.data_list)

        plot_target_memory_time_x_y_2D(ax2, element.data_list)
        plot_target_memory_time_x_y_3D(ax1, element.data_list)


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

    def __eq__(self, other):
        return self.target_id == other.target_id

    def __lt__(self, other):
        return self.target_id < other.target_id

    def __gt__(self, other):
        return self.target_id > other.target_id


class AnalyseMemoryAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.data = load_csv_file_dictionnary(PATH_LOAD_DATA + str(agent_id))
        self.simulated_data = load_csv_file_dictionnary(PATH_LOAD_DATA_REF)
        self.data_sort_by_target = []
        self.simulated_data_sort_by_target = []

        sort_by_target(self.data, self.data_sort_by_target)
        sort_by_target(self.simulated_data, self.simulated_data_sort_by_target)

    def plot_all_target_simulated_data_collected_data(self):
        fig_time_type_x_y = plt.figure(figsize=(12, 8), tight_layout=True)
        fig_time_type_x_y.suptitle('Agent ' + str(self.id), fontsize=17, fontweight='bold', y=1)
        fig_time_type_x_y.subplots_adjust(bottom=0.06, left=0.05, right=0.98, top=0.95)
        ax1 = fig_time_type_x_y.add_subplot(2, 2, 1)
        ax2 = fig_time_type_x_y.add_subplot(2, 2, 2)
        ax3 = fig_time_type_x_y.add_subplot(2, 2, 3)
        ax4 = fig_time_type_x_y.add_subplot(2, 2, 4)

        for element in self.simulated_data_sort_by_target:
            sc1 = plot_target_memory_time_x_y_2D(ax1, element.data_list,
                                                 curve_label="target" + str(element.target_id))

        for element in self.data_sort_by_target:
            plot_target_memory_x_y(ax1, element.data_list, curve_label="target" + str(element.target_id))
            sc2 = plot_target_memory_type_x_y_2D(ax2, element.data_list,
                                                 curve_label="target" + str(element.target_id))
            sc3 = plot_target_memory_agent_x_y_2D(ax3, element.data_list,
                                                  curve_label="target" + str(element.target_id))
            plot_target_memory_time_agent(ax4, element.data_list, curve_label="target" + str(element.target_id))

        fig_time_type_x_y.colorbar(sc1, ax=ax1)
        fig_time_type_x_y.colorbar(sc2, ax=ax2)
        fig_time_type_x_y.colorbar(sc3, ax=ax3)

        fig_time_type_x_y.savefig(PATH_SAVE_PLOT + VERSION_SAVE_PLOT + "agent_" + str(self.id), transparent=False)

    def plot_a_target_simulated_data_collected_data(self, target_id):
        fig_time_type_x_y = plt.figure(figsize=(12, 8), tight_layout=True)
        fig_time_type_x_y.suptitle('Agent ' + str(self.id), fontsize=17, fontweight='bold', y=1)
        fig_time_type_x_y.subplots_adjust(bottom=0.06, left=0.05, right=0.98, top=0.95)
        ax1 = fig_time_type_x_y.add_subplot(2, 2, 1)
        ax2 = fig_time_type_x_y.add_subplot(2, 2, 2)
        ax3 = fig_time_type_x_y.add_subplot(2, 2, 3)
        ax4 = fig_time_type_x_y.add_subplot(2, 2, 4)

        for element in self.simulated_data_sort_by_target:
            if target_id == int(element.target_id):
                sc1 = plot_target_memory_time_x_y_2D(ax1, element.data_list,
                                                     curve_label="target" + str(element.target_id))

        for element in self.data_sort_by_target:
            if target_id == int(element.target_id):
                plot_target_memory_x_y(ax1, element.data_list, curve_label="target" + str(element.target_id))
                sc2 = plot_target_memory_type_x_y_2D(ax2, element.data_list,
                                                     curve_label="target" + str(element.target_id))
                sc3 = plot_target_memory_agent_x_y_2D(ax3, element.data_list,
                                                      curve_label="target" + str(element.target_id))
                plot_target_memory_time_agent(ax4, element.data_list,
                                              curve_label="target" + str(element.target_id))

        fig_time_type_x_y.colorbar(sc1, ax=ax1)
        fig_time_type_x_y.colorbar(sc2, ax=ax2)
        fig_time_type_x_y.colorbar(sc3, ax=ax3)
        fig_time_type_x_y.savefig(PATH_SAVE_PLOT + VERSION_SAVE_PLOT + "agent_" + str(self.id) + "-target_" + str(target_id),
                                  transparent=False)
