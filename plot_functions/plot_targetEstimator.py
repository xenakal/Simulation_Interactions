import constants
from multi_agent.agent.agent_interacting_room_camera import AgentCam
from my_utils.my_IO.IO_data import *
from my_utils.my_math.MSE import *

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
RADIUS_INDEX = 13


def plot_target_memory_type_x_y_2D(ax, data, curve_label):
    return plot_graph_3D_2D(ax, data[X_INDEX], data[Y_INDEX], data[TYPE_INDEX], data[RADIUS_INDEX], 0, 4, "x-y plane, type", "x [m]", "y [m]",
                            curve_label=curve_label)


def plot_target_memory_time_x_y_2D(ax, data, curve_label="curve_label"):
    return plot_graph_3D_2D(ax, data[X_INDEX], data[Y_INDEX], data[TIME_INDEX], data[RADIUS_INDEX], T_MIN, T_MAX, "x-y plane, time", "x [m]", "y [m]",
                            curve_label=curve_label)


def plot_target_memory_agent_x_y_2D(ax, data, curve_label="curve_label"):
    return plot_graph_3D_2D(ax, data[X_INDEX], data[Y_INDEX], data[AGENT_INDEX], data[RADIUS_INDEX], 0, AgentCam.number_agentCam_created-1, "x-y plane agent",
                            "x [m]", "y [m]", curve_label=curve_label)


def plot_target_memory_agent_vx_vy_2D(ax, data, curve_label="curve_label"):
    return plot_graph_3D_2D(ax, data[VX_INDEX], data[VY_INDEX], data[AGENT_INDEX], data[RADIUS_INDEX], 0, AgentCam.number_agentCam_created-1, "x-y plane agent",
                            "vx [m/s]", "vy [m/s]", curve_label=curve_label)


def plot_target_memory_agent_ax_ay_2D(ax, data, curve_label="curve_label"):
    return plot_graph_3D_2D(ax, data[AX_INDEX], data[AY_INDEX], data[AGENT_INDEX], data[RADIUS_INDEX], 0, 2, "x-y plane agent",
                            "ax [m/s^2]", "ay [m/s^2]", curve_label=curve_label)


def plot_target_memory_x_y(ax, data, curve_label="curve_label"):
    plot_graph_x_y(ax, data[X_INDEX], data[Y_INDEX], "x-y plane, time", "x [m]", "y [m]", curve_label=curve_label)


def plot_target_memory_time_x(ax, data, curve_label="curve_label"):
    plot_graph_time_x(ax, data[TIME_INDEX], data[X_INDEX], "X in terms of time", "time [s]", "x [m]", curve_label=curve_label)


def plot_target_memory_time_y(ax, data, curve_label="curve_label"):
    plot_graph_time_x(ax, data[TIME_INDEX], data[Y_INDEX], "Y in terms of time", "time [s]", "y [m]", curve_label=curve_label)


def plot_target_memory_time_agent(ax, data, curve_label="curve_label"):
    plot_graph_time_x(ax, data[TIME_INDEX], data[AGENT_INDEX], "Agent generating info in terms of time", "time [s]", "Agent [id]",
                      curve_label=curve_label)


def plot_target_memory_type_x_y_3D(ax, data):
    plot_graph_3D(ax, data[X_INDEX], data[Y_INDEX], data[TIME_INDEX], "x-y plane, type", "x [m]", "y [m]")


def plot_target_memory_time_x_y_3D(ax, data):
    plot_graph_3D(ax, data[X_INDEX], data[Y_INDEX], data[TIME_INDEX], "x-y plane, time", "x [m]", "y [m]")


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
                if (i == 6 or i == 7) and data[constants.TARGET_ESTIMATOR_CSV_FIELDNAMES[i]][0] == "[":
                    data[constants.TARGET_ESTIMATOR_CSV_FIELDNAMES[i]] = data[constants.TARGET_ESTIMATOR_CSV_FIELDNAMES[
                        i]][1:-1]

                self.data_list[i].append(float(data[constants.TARGET_ESTIMATOR_CSV_FIELDNAMES[i]]))
            except ValueError:
                print("problème")
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


class Analyser_Target_TargetEstimator_FormatCSV:
    def __init__(self, agent_id, path_to_load_data,path_to_save_data, version="version"):
        self.id = agent_id
        self.version = version
        self.path_to_save_data = path_to_save_data
        self.data = load_csv_file_dictionnary(path_to_load_data + str(agent_id))
        self.simulated_data = load_csv_file_dictionnary(constants.ResultsPath.DATA_REFERENCE)
        self.data_sort_by_target = []
        self.simulated_data_sort_by_target = []

        init_analyse_memory_agent(self.data, self.data_sort_by_target)
        init_analyse_memory_agent(self.simulated_data, self.simulated_data_sort_by_target)

    def plot_MSE_prediction_1_target_id(self, target_id):
        try:
            data_ref = []
            data_mes = []

            for element in self.simulated_data_sort_by_target:
                if target_id == int(element.target_id):
                    data_ref = element.data_list

            for element in self.data_sort_by_target:
                if target_id == int(element.target_id):
                    data_mes = element.data_list

            (t_ref, x_ref, y_ref, x_mes, y_mes, error_squared_x) = get_comparable_data_btw_reference_mesure(data_ref,data_mes)
            """to put the prediction on the real data"""
            x_ref = x_ref[1:]
            y_ref = y_ref[1:]
            t_ref = t_ref[1:]

            x_mes = x_mes[1:]
            y_mes = y_mes[1:]
            t_mes = t_ref[1:]

            error_squared_x = error_squared_list(x_ref, x_mes)
            error_squared_y = error_squared_list(y_ref, y_mes)
            error_squared = error_squared_x_y_list(x_ref, y_ref, x_mes, y_mes)

            self.plot_MES_target_id(target_id, t_ref, x_ref, y_ref, x_mes, y_mes, error_squared_x, error_squared_y,
                                    error_squared)

        except:
            print("plot error : plot_MSE_prediction_1_target_id ")

    def plot_MSE_prediction_2_target_id(self, target_id):

        try:
            data_ref = []
            data_mes = []

            for element in self.simulated_data_sort_by_target:
                if target_id == int(element.target_id):
                    data_ref = element.data_list

            for element in self.data_sort_by_target:
                if target_id == int(element.target_id):
                    data_mes = element.data_list

            (t_ref, x_ref, y_ref, x_mes, y_mes, error_squared_x) = get_comparable_data_btw_reference_mesure(data_ref,
                                                                                                            data_mes)
            """to put the prediction on the real data"""
            x_ref = x_ref[2:]
            y_ref = y_ref[2:]
            t_ref = t_ref[2:]

            x_mes = x_mes[2:]
            y_mes = y_mes[2:]
            t_mes = t_ref[2:]

            error_squared_x = error_squared_list(x_ref, x_mes)
            error_squared_y = error_squared_list(y_ref, y_mes)
            error_squared = error_squared_x_y_list(x_ref, y_ref, x_mes, y_mes)

            self.plot_MES_target_id(target_id, t_ref, x_ref, y_ref, x_mes, y_mes, error_squared_x, error_squared_y,
                                    error_squared)
        except:
            print("plot error:  plot_MSE_prediction_2_target_id")

    def plot_MSE_not_interpolate_target_id(self, target_id):
        data_ref = []
        data_mes = []

        for element in self.simulated_data_sort_by_target:
            if target_id == int(element.target_id):
                data_ref = element.data_list

        for element in self.data_sort_by_target:
            if target_id == int(element.target_id):
                data_mes = element.data_list

        try:
            (t_ref, x_ref, y_ref, x_mes, y_mes, error_squared_x, error_squared_y, error_squared) = error_squared_discrete(
                data_ref, data_mes)

            self.plot_MES_target_id(target_id, t_ref, x_ref, y_ref, x_mes, y_mes, error_squared_x, error_squared_y,
                                    error_squared)
        except:
            print("error plot : plot_MSE_not_interpolate_target_id")

    def plot_MSE_interpolate_target_id(self,target_id):
        try:
            data_ref = []
            data_mes = []

            for element in self.simulated_data_sort_by_target:
                if target_id == int(element.target_id):
                    data_ref = element.data_list

            for element in self.data_sort_by_target:
                if target_id == int(element.target_id):
                    data_mes = element.data_list

            (t_ref, x_ref, y_ref, x_mes, y_mes) = error_squared_with_interpolation(data_ref, data_mes)

            fig = plt.figure(figsize=(12, 8))
            fig.suptitle('Agent ' + str(self.id), fontsize=17, fontweight='bold', y=0.98)
            fig.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
            ax1 = fig.add_subplot(1, 2, 1)
            ax2 = fig.add_subplot(1, 2, 2)


            sc1 = ax1.scatter(np.array(x_ref), np.array(y_ref), c=np.array(t_ref),
                             s=2500 * math.pow(data_ref[RADIUS_INDEX][0], 2) * math.pi, vmin=T_MIN, vmax=T_MAX, cmap="Spectral",
                            alpha=0.4)
            sc2 = ax2.scatter(np.array(x_mes), np.array(y_mes), c=np.array(t_ref),
                             s=2500 * math.pow(data_ref[RADIUS_INDEX][0], 2) * math.pi, vmin=T_MIN, vmax=T_MAX,
                             cmap="Spectral",
                             alpha=0.4)

            fig.colorbar(sc1, ax=ax1)
            fig.colorbar(sc2, ax=ax2)
            fig.savefig(self.path_to_save_data + self.version + "--Interpolation_agent_" + str(self.id),
                                 transparent=False)
            plt.close(fig)
        except:
            print("error plot : plot_MSE_interpolate_target_id")

    def plot_MES_target_id(self,target_id, t_ref,x_ref,y_ref,x_mes,y_mes,error_squared_x,error_squared_y,error_squared) :

        try:
            fig = plt.figure(figsize=(12, 8), tight_layout=True)

            ax = fig.add_subplot(3, 2, (1, 3))
            ax1 = fig.add_subplot(3, 2, (5, 6))
            ax2 = fig.add_subplot(3, 2, 2)
            ax3 = fig.add_subplot(3, 2, 4)

            mean_error_squared_x = np.mean(error_squared_x)
            mean_error_squared_y = np.mean(error_squared_y)
            mean_error_squared_x_y = np.mean(error_squared)

            sc = ax.scatter(x_ref, y_ref, s=100, c=t_ref, cmap="Spectral", alpha=0.4)
            plot_graph_time_x(ax, x_ref, y_ref, "Trajectory", "x [m]", "y [m]", curve_label="interpolation_ref")
            plot_graph_x_y(ax, x_mes, y_mes, "Trajectory", "x [m]", "y [m]",curve_label="interpolation_mes")
            plot_graph_time_x(ax1, t_ref, error_squared, "squared error norm  x-y", "time [s]", "[m^2]",curve_label="t_value")
            plot_graph_time_x(ax2, t_ref, error_squared_x, "squared error norm  x", "time [s]", "[m^2]",curve_label="t_value")
            plot_graph_time_x(ax3, t_ref, error_squared_y, "squared norm  y", "time [s]", "[m^2]", curve_label="t_value")

            plot_graph_time_x(ax1, t_ref, mean_error_squared_x_y * np.ones(np.size(t_ref)),
                              "squared error norm  x-y","time [s]", "[m^2]",curve_label="mean")
            plot_graph_time_x(ax2, t_ref, mean_error_squared_x * np.ones(np.size(t_ref)), "squared error norm  x",
                              "time [s]", "[m^2]",
                              curve_label="mean")
            plot_graph_time_x(ax3, t_ref, mean_error_squared_y * np.ones(np.size(t_ref)), "squared norm  y", "time [s]",
                              "[m^2]", curve_label="mean")


            (yb, yh) = ax1.get_ylim()
            ax1.text(0, yh, "mean error = %.2f" % (np.sqrt(mean_error_squared_x_y)), fontweight='bold', fontsize=10)

            (yb, yh) = ax2.get_ylim()
            ax2.text(0, yb, "mean error = %.2f" % (np.sqrt(mean_error_squared_x)), fontweight='bold', fontsize=10)

            (yb, yh) = ax3.get_ylim()
            ax3.text(0, yb, "mean error = %.2f" % (np.sqrt(mean_error_squared_y)), fontweight='bold', fontsize=10)

            fig.colorbar(sc, ax=ax)
            fig.savefig(self.path_to_save_data + self.version + "--MSE_agent_" + str(self.id)+ "-target_" + str(target_id), transparent=False)
            plt.close(fig)
        except:
            print("error plot : plot_MES_target_id")



    def plot_position_target_simulated_data_collected_data(self):

        try:
            fig_position = plt.figure(figsize=(12, 8))
            fig_position.suptitle('Agent ' + str(self.id), fontsize=17, fontweight='bold', y=0.98)
            fig_position.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
            ax1 = fig_position.add_subplot(1, 2, 1)
            ax2 = fig_position.add_subplot(1, 2, 2)

            for element in self.simulated_data_sort_by_target:
                sc1 = plot_target_memory_time_x_y_2D(ax1, element.data_list,
                                                     curve_label="target" + str(element.target_id))

            for element in self.data_sort_by_target:
                sc2 = plot_target_memory_time_x_y_2D(ax2, element.data_list,
                                                     curve_label="target" + str(element.target_id))
            fig_position.colorbar(sc1, ax=ax1)
            fig_position.colorbar(sc2, ax=ax2)
            fig_position.savefig(self.path_to_save_data + self.version + "--position_agent_" + str(self.id),
                transparent=False)
            plt.close(fig_position)
        except:
            print("error plot :  plot_position_target_simulated_data_collected_data")


    def plot_all_target_simulated_data_collected_data(self):
        fig_time_type_x_y = plt.figure(figsize=(12, 8), tight_layout=True)
        fig_time_type_x_y.suptitle('Agent ' + str(self.id), fontsize=17, fontweight='bold', y=1)
        ax1 = fig_time_type_x_y.add_subplot(2, 2, 1)
        ax2 = fig_time_type_x_y.add_subplot(2, 2, 2)
        ax3 = fig_time_type_x_y.add_subplot(2, 2, 3)
        ax4 = fig_time_type_x_y.add_subplot(2, 2, 4)
        try:

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

            fig_time_type_x_y.savefig(self.path_to_save_data + self.version + "--general_agent_" + str(self.id),
                transparent=False)
            plt.close(fig_time_type_x_y)

        except:
            print("error plot: plot_all_target_simulated_data_collected_data")

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
            fig_time_type_x_y.savefig(self.path_to_save_data + self.version + "--general_agent_" + str(
                    self.id) + "-target_" + str(target_id), transparent=False)
        except:
            print("plot_a_target_simulated_data_collected_data")

        plt.close(fig_time_type_x_y)


class Analyser_Agent_Target_TargetEstimator_FormatCSV:
    def __init__(self, agent_id, path_to_load_data, path_to_save_data, version="version"):
        self.id = agent_id
        self.version = version
        self.path_to_save_data = path_to_save_data
        self.data = load_csv_file_dictionnary(path_to_load_data + str(agent_id))
        self.simulated_data = load_csv_file_dictionnary(constants.ResultsPath.DATA_REFERENCE)
        self.data_sort_by_agent_target = []
        self.simulated_data_sort_by_target = []

        init_analyse_memory_all_agent(self.data, self.data_sort_by_agent_target)
        init_analyse_memory_agent(self.simulated_data, self.simulated_data_sort_by_target)

    def plot_position_target_simulated_data_collected_data(self):
        try:
            fig_position = plt.figure(figsize=(12, 8))
            fig_position.suptitle('Agent ' + str(self.id), fontsize=17, fontweight='bold', y=0.98)
            fig_position.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
            ax1 = fig_position.add_subplot(1, 2, 1)
            ax2 = fig_position.add_subplot(1, 2, 2)

            for element in self.simulated_data_sort_by_target:
                sc1 = plot_target_memory_time_x_y_2D(ax1, element.data_list,
                                                     curve_label="target" + str(element.target_id))

            for element_agent in self.data_sort_by_agent_target:
                for element_target in element_agent.data_list:
                    sc2 = plot_target_memory_time_x_y_2D(ax2, element_target.data_list,
                                                         curve_label="agent" + str(
                                                             element_agent.agent_id) + "-target" + str(
                                                             element_target.target_id))

            fig_position.colorbar(sc1, ax=ax1)
            fig_position.colorbar(sc2, ax=ax2)

            fig_position.savefig(
                constants.ResultsPath.SAVE_LOAD_PLOT_MEMORY_ALL_AGENT + self.version + "--position_all_agent_" + str(
                    self.id),
                transparent=False)
            plt.close(fig_position)
        except:
            print("plot_position_target_simulated_data_collected_data")

    def plot_all_target_simulated_data_collected_data(self):
        try:
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

            fig_time_type_x_y.savefig(
                constants.ResultsPath.SAVE_LOAD_PLOT_MEMORY_ALL_AGENT + self.version + "--general_agent_" + str(self.id),
                transparent=False)
            plt.close(fig_time_type_x_y)
        except:
            print("plot_all_target_simulated_data_collected_data")
