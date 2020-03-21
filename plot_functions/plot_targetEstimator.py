from plot_functions.plot_toolbox import *
import constants




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


def init_analyse_memory_agent(list_init, list_sort):
    for data_element in list_init:
        is_in_list = False
        for element in list_sort:
            if int(data_element['target_signature']) == element.target_signature:
                element.add_target_estimator(data_element)
                is_in_list = True
                break
        if not is_in_list:
            "Create a new TargetSortedTargetEstimator"
            target_created = TargetSortedTargetEstimator(data_element['target_id'],
                                                         data_element['target_signature'])
            "Add Data"
            target_created.add_target_estimator(data_element)
            list_sort.append(target_created)

    list_sort.sort()


def init_analyse_memory_all_agent(list_init, list_sort):
    for data_element in list_init:
        is_in_list_agent = False
        is_in_list_target = False

        for agent_element in list_sort:
            if agent_element.agent_signature == int(data_element['agent_signature']):
                is_in_list_agent = True
                for target_element in agent_element.data_list:
                    if target_element.target_signature == int(data_element['target_signature']):
                        is_in_list_target = True

                        "Add Data"
                        target_element.add_target_estimator(data_element)
                        break

                if not is_in_list_target:
                    "Create a new TargetSortedTargetEstimator"
                    target_created = TargetSortedTargetEstimator(data_element['target_id'],
                                                                 data_element['target_signature'])
                    "Add Data"
                    target_created.add_target_estimator(data_element)
                    agent_element.data_list.append(target_created)

                break

        if not is_in_list_agent:
            "Create a new AgentSortedTargetEstimator"
            agent_created = AgentSortedTargetEstimator(data_element['agent_id'], data_element['agent_signature'])
            "Create a new TargetSortedTargetEstimator"
            target_created = TargetSortedTargetEstimator(data_element['target_id'], data_element['target_signature'])
            "Add the new data"
            target_created.add_target_estimator(data_element)
            agent_created.data_list.append(target_created)
            list_sort.append(agent_created)

    list_sort.sort()
    for elem in list_sort:
        elem.data_list.sort()

class TargetSortedTargetEstimator:
    def __init__(self, target_id, target_signature):
        self.target_id = int(target_id)
        self.target_signature = int(target_signature)
        self.data_list = []
        self.init()

    def init(self):
        for i in range(len(constants.TARGET_ESTIMATOR_CSV_FIELDNAMES)):
            self.data_list.append([])

    def add_target_estimator(self, data):
        for i in range(len(constants.TARGET_ESTIMATOR_CSV_FIELDNAMES)):
            try:
                self.data_list[i].append(int(float(data[constants.TARGET_ESTIMATOR_CSV_FIELDNAMES[i]])))
            except ValueError:
                self.data_list[i].append(data[constants.TARGET_ESTIMATOR_CSV_FIELDNAMES[i]])

    def __eq__(self, other):
        return self.target_id == other.target_id

    def __lt__(self, other):
        return self.target_id < other.target_id

    def __gt__(self, other):
        return self.target_id > other.target_id


class AgentSortedTargetEstimator:
    def __init__(self, agent_id, agent_signature):
        self.agent_id = int(agent_id)
        self.agent_signature = int(agent_signature)
        self.data_list = []

    def __eq__(self, other):
        return self.agent_signature == other.agent_signature

    def __lt__(self, other):
        return self.agent_signature < other.agent_signature

    def __gt__(self, other):
        return self.agent_signature > other.agent_signature


class AnalyseMemoryAgent:
    def __init__(self, agent_id,version = "version"):
        self.id = agent_id
        self.version = version

        self.data = load_csv_file_dictionnary(constants.SavePlotPath.SAVE_LOAD_DATA_MEMORY_AGENT + str(agent_id))
        self.simulated_data = load_csv_file_dictionnary(constants.SavePlotPath.DATA_REFERENCE)
        self.data_sort_by_target = []
        self.simulated_data_sort_by_target = []

        init_analyse_memory_agent(self.data, self.data_sort_by_target)
        init_analyse_memory_agent(self.simulated_data, self.simulated_data_sort_by_target)

    def plot_position_target_simulated_data_collected_data(self):
        fig_position = plt.figure(figsize=(12, 8))
        fig_position.suptitle('Agent ' + str(self.id), fontsize=17, fontweight='bold', y=0.98)
        fig_position.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
        ax1 = fig_position.add_subplot(1, 1, 1)

        for element in self.simulated_data_sort_by_target:
            sc1 = plot_target_memory_time_x_y_2D(ax1, element.data_list,
                                                 curve_label="target" + str(element.target_id))

        for element in self.data_sort_by_target:
            plot_target_memory_x_y(ax1, element.data_list, curve_label="target" + str(element.target_id))

        fig_position.colorbar(sc1, ax=ax1)
        fig_position.savefig(constants.SavePlotPath.SAVE_LOAD_PLOT_MEMORY_AGENT + self.version + "--position_agent_" + str(self.id),
                                  transparent=False)
        plt.close(fig_position)

    def plot_all_target_simulated_data_collected_data(self):
        fig_time_type_x_y = plt.figure(figsize=(12, 8), tight_layout=True)
        fig_time_type_x_y.suptitle('Agent ' + str(self.id), fontsize=17, fontweight='bold', y=1)
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

        fig_time_type_x_y.savefig(constants.SavePlotPath.SAVE_LOAD_PLOT_MEMORY_AGENT + self.version + "--all_agent_" + str(self.id),
                                  transparent=False)
        plt.close(fig_time_type_x_y)

    def plot_a_target_simulated_data_collected_data(self, target_id):
        fig_time_type_x_y = plt.figure(figsize=(12, 8), tight_layout=True)
        fig_time_type_x_y.suptitle('Agent ' + str(self.id), fontsize=17, fontweight='bold', y=1)
        ax1 = fig_time_type_x_y.add_subplot(2, 2, 1)
        ax2 = fig_time_type_x_y.add_subplot(2, 2, 2)
        ax3 = fig_time_type_x_y.add_subplot(2, 2, 3)
        ax4 = fig_time_type_x_y.add_subplot(2, 2, 4)

        try:
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
            fig_time_type_x_y.savefig(
                constants.SavePlotPath.SAVE_LOAD_PLOT_MEMORY_AGENT + self.version + "--all_agent_" + str(self.id) + "-target_" + str(
                    target_id),
                transparent=False)


        except:
            print("error in plot_a_target_simulated_data_collected_data agent" + str(self.id) + " target " + str(
                target_id))

        plt.close(fig_time_type_x_y)

class AnalyseAllMemoryAgent:
    def __init__(self, agent_id,version="version"):
        self.id = agent_id
        self.version = version
        self.data = load_csv_file_dictionnary(constants.SavePlotPath.SAVE_LOAD_DATA_MEMORY_ALL_AGENT+ str(agent_id))
        self.simulated_data = load_csv_file_dictionnary(constants.SavePlotPath.DATA_REFERENCE)
        self.data_sort_by_agent_target = []
        self.simulated_data_sort_by_target = []

        init_analyse_memory_all_agent(self.data, self.data_sort_by_agent_target)
        init_analyse_memory_agent(self.simulated_data, self.simulated_data_sort_by_target)

    def plot_position_target_simulated_data_collected_data(self):
        fig_position = plt.figure(figsize=(12, 8))
        fig_position.suptitle('Agent ' + str(self.id), fontsize=17, fontweight='bold', y=0.98)
        fig_position.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
        ax1 = fig_position.add_subplot(1, 1, 1)


        for element in self.simulated_data_sort_by_target:
            sc1 = plot_target_memory_time_x_y_2D(ax1, element.data_list,
                                                 curve_label="target" + str(element.target_id))

        for element_agent in self.data_sort_by_agent_target:
            for element_target in element_agent.data_list:
                plot_target_memory_x_y(ax1, element_target.data_list, curve_label="agent-" + str(element_agent.agent_id)
                                                                                  + ",target-" + str(
                    element_target.target_id))

        fig_position.colorbar(sc1, ax=ax1)

        fig_position.savefig(constants.SavePlotPath.SAVE_LOAD_PLOT_MEMORY_ALL_AGENT + self.version + "--position_agent_" + str(self.id),
                                  transparent=False)
        plt.close(fig_position)

    def plot_all_target_simulated_data_collected_data(self):
        fig_time_type_x_y = plt.figure(figsize=(12, 8), tight_layout=True)
        fig_time_type_x_y.suptitle('Agent ' + str(self.id), fontsize=17, fontweight='bold', y=1)
        ax1 = fig_time_type_x_y.add_subplot(2, 2, 1)
        ax2 = fig_time_type_x_y.add_subplot(2, 2, 2)
        ax3 = fig_time_type_x_y.add_subplot(2, 2, 3)
        ax4 = fig_time_type_x_y.add_subplot(2, 2, 4)

        for element in self.simulated_data_sort_by_target:
            sc1 = plot_target_memory_time_x_y_2D(ax1, element.data_list,
                                                 curve_label="target" + str(element.target_id))

        for element_agent in self.data_sort_by_agent_target:
            for element_target in element_agent.data_list:
                plot_target_memory_x_y(ax1, element_target.data_list, curve_label="agent-" + str(element_agent.agent_id)
                                                                                  + ",target-" + str(
                    element_target.target_id))
                sc2 = plot_target_memory_type_x_y_2D(ax2, element_target.data_list,
                                                     curve_label="agent-" + str(element_agent.agent_id)
                                                                 + ",target-" + str(element_target.target_id))
                sc3 = plot_target_memory_agent_x_y_2D(ax3, element_target.data_list,
                                                      curve_label="agent-" + str(element_agent.agent_id)
                                                                  + ",target-" + str(element_target.target_id))
                plot_target_memory_time_agent(ax4, element_target.data_list,
                                              curve_label="agent-" + str(element_agent.agent_id)
                                                          + ",target-" + str(element_target.target_id))

        fig_time_type_x_y.colorbar(sc1, ax=ax1)
        fig_time_type_x_y.colorbar(sc2, ax=ax2)
        fig_time_type_x_y.colorbar(sc3, ax=ax3)

        fig_time_type_x_y.savefig(constants.SavePlotPath.SAVE_LOAD_PLOT_MEMORY_ALL_AGENT + self.version + "--all_agent_" + str(self.id),
                                  transparent=False)
        plt.close(fig_time_type_x_y)

