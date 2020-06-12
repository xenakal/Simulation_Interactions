import math
from src import constants
from src.plot_functions.plot_agentEstimator import AgentEstimatorPloter
from src.plot_functions.plot_controller import ControllerPlot, plot_scenario, plot_scenario_last
from src.plot_functions.plot_targetEstimator import Analyser_Target_TargetEstimator_FormatCSV
import matplotlib.pyplot as plt
import numpy as np
constants.ResultsPath.folder =  "../../to_share"
constants.ResultsPath.name_simulation = "controller-attractive-mode"

#constants.ResultsPath.folder = "../../results"
#constants.ResultsPath.name_simulation = "Super_use-case"

target_ploter = analyser_simulated_data = Analyser_Target_TargetEstimator_FormatCSV("",
                                                                        constants.ResultsPath.SAVE_LOAD_DATA_REFERENCE,
                                                                        constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER)

user_plotter = Analyser_Target_TargetEstimator_FormatCSV(100, constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_AGENT,
                                                               constants.ResultsPath.SAVE_LOAD_PLOT_MEMORY_AGENT)

controller_ploter_0 = ControllerPlot(0)


fig = plt.figure(figsize=(12, 8),tight_layout = True)
fig50 = plt.figure(figsize=(12, 8),tight_layout = True)
ax = fig.add_subplot(1, 1, 1)
ax50 = fig50.add_subplot(1, 1, 1)
colors = ["green","orangered"]
for element,color in zip(target_ploter.simulated_data_sort_by_target,colors):
    sc = ax.scatter(element.data_list[7], element.data_list[8], c= np.array(element.data_list[0]), s=500, cmap="Spectral",
                     alpha=0.3)
    ax.scatter(element.data_list[7], element.data_list[8], marker='x',color=color, edgecolors='gold', alpha=0.6,s = 100)

cb = fig.colorbar(sc, ax=ax)
cb.ax.tick_params(labelsize=15)
cb.ax.set_xlabel("time [s]", fontsize=20)
ax.xaxis.set_tick_params(labelsize=20)
ax.yaxis.set_tick_params(labelsize=20)
ax.set_xlabel("x [m]", fontsize=20)
ax.set_ylabel("y [m]", fontsize=20)
ax.set_title("", fontsize=25, fontweight='bold')
ax.grid(True)
ax.set_xbound(-1,11)
ax.set_ybound(-1,11)


fig2 = plt.figure(figsize=(12, 8),tight_layout = True)
ax2 = fig2.add_subplot(1, 1, 1)

for element,color in zip(target_ploter.simulated_data_sort_by_target,colors):
    sc = ax2.scatter(element.data_list[7], element.data_list[8], c= np.array(element.data_list[0]), s=500, cmap="Spectral",
                     alpha=0.1)
    sc = ax50.scatter(element.data_list[7], element.data_list[8], c=np.array(element.data_list[0]), s=500,
                     cmap="Spectral",
                     alpha=1)
    ax2.scatter(element.data_list[7], element.data_list[8], marker='x',color=color, edgecolors='gold', alpha=0.3,s = 100)

for element,color in zip(user_plotter.data_sort_by_target,colors):
        ax2.scatter(element.data_list[7], element.data_list[8],  marker='o',color=color, edgecolors='black', alpha=0.3,s = 100)

plot_scenario(fig2,ax2,controller_ploter_0.data)

cb = fig2.colorbar(sc, ax=ax2)
cb.ax.tick_params(labelsize=15)
cb.ax.set_ylabel("time [s]", fontsize=20)
ax2.xaxis.set_tick_params(labelsize=20)
ax2.yaxis.set_tick_params(labelsize=20)
ax2.set_xlabel("x [m]", fontsize=20)
ax2.set_ylabel("y [m]", fontsize=20)
ax2.set_title("", fontsize=25, fontweight='bold')
ax2.grid(True)
ax2.set_xbound(-1,11)
ax2.set_ybound(-1,11)




fig3 = plt.figure(figsize=(12, 8),tight_layout = True)
ax3 = fig3.add_subplot(1, 1, 1)
for color in colors:
    ax3.scatter(0, 0, marker='x', color=color, edgecolors='black',s = 100)
for color in colors:
    ax3.scatter(0, 0, marker='o', color=color, edgecolors='black',s = 100)
ax3.scatter(0, 0, marker='D', s=100, c='gold', edgecolors='black')
ax3.scatter(0, 0, marker='*', s=100, c='orangered', edgecolors='black')
ax3.legend(["generated position of target 0","generated position of target 1","filtered position of target 0",
            "filtered of target 1","positions of the cameras","argeted positions of the cameras"], fontsize=20,loc=3)





fig4 = plt.figure(figsize=(10,8), tight_layout=True)
# fig.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
ax1 = fig4.add_subplot(3,1, 1)
ax2 = fig4.add_subplot(3,1, 2)
ax3 = fig4.add_subplot(3,1, 3)

sc1 = ax1.scatter(controller_ploter_0.data[0], controller_ploter_0.data[5], marker='*', s=200, c='orangered', edgecolors='red')
sc1 = ax1.scatter(controller_ploter_0.data[0], controller_ploter_0.data[1], marker='D', s=50, c='gold', edgecolors='red', alpha=0.5)
ax1.legend(["x_targeted", "x_measured"], fontsize=20)
ax1.set_title("x-coordinate in terms of time", fontsize=20, fontweight='bold')
ax1.set_xlabel("time [s]", fontsize=20)
ax1.set_ylabel("x [m]", fontsize=20)

sc2 = ax2.scatter(controller_ploter_0.data[0], controller_ploter_0.data[6], marker='*', s=200, c='orangered', edgecolors='blue')
sc2 = ax2.scatter(controller_ploter_0.data[0], controller_ploter_0.data[2], marker='D', s=50, c='gold', edgecolors='blue', alpha=0.5)
ax2.legend(["y_targeted", "y_measured"], fontsize=20)
ax2.set_title("y-coordinate in terms of time", fontsize=20, fontweight='bold')
ax2.set_xlabel("time [s]", fontsize=20)
ax2.set_ylabel("y [m]", fontsize=20)

sc3 = ax3.scatter(controller_ploter_0.data[0], np.array(controller_ploter_0.data[7]) * 180 / math.pi, marker='*', s=200, c='orangered', edgecolors='green')
sc3 = ax3.scatter(controller_ploter_0.data[0], np.array(controller_ploter_0.data[3]) * 180 / math.pi, marker='D', s=50, c='gold', edgecolors='green', alpha=0.5)
ax3.legend(["alpha_targeted", "alpha_measured"], fontsize=20)
ax3.set_title("alpha-coordinate in terms of time", fontsize=20, fontweight='bold')
ax3.set_xlabel("time [s]", fontsize=20)
ax3.set_ylabel("alpha [°]", fontsize=20)

ax1.xaxis.set_tick_params(labelsize=15)
ax1.yaxis.set_tick_params(labelsize=15)
ax2.xaxis.set_tick_params(labelsize=15)
ax2.yaxis.set_tick_params(labelsize=15)
ax3.xaxis.set_tick_params(labelsize=15)
ax3.yaxis.set_tick_params(labelsize=15)


ax1.grid(True)
ax2.grid(True)
ax3.grid(True)
ax.set_xbound(-1, 11)
ax.set_ybound(-1, 11)

fig5 = plt.figure(figsize=(10,8), tight_layout=True)
ax4 = fig5.add_subplot(1,1,1)
sc4 = ax4.scatter(controller_ploter_0.data[0], np.array(controller_ploter_0.data[9]) * 100, marker='o', c='red',edgecolors='black')
sc4 = ax4.scatter(controller_ploter_0.data[0], np.array(controller_ploter_0.data[10]) * 100, marker='o', c='blue',edgecolors='black')
sc4 = ax4.scatter(controller_ploter_0.data[0], np.array(controller_ploter_0.data[11]) * 100, marker='o', c='green',edgecolors='black')
# sc4 = ax4.plot(data[0], np.array(data[12])*100, '.', color='gold')
ax4.set_title("controller command in terms of time", fontsize=20, fontweight='bold')
ax4.set_xlabel("time [s]", fontsize=20)
ax4.set_ylabel("command [%]", fontsize=20)
ax4.legend(["x_command", "y_command", "alpha_command"], fontsize=20)


fig.savefig(constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER + "-- target")
fig2.savefig(constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER + "-- agent")
fig3.savefig(constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER + "-- legend")
fig4.savefig(constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER + "--  dof")
fig5.savefig(constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER + "-- gain")

plt.show()




