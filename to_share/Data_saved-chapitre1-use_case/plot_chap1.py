from src import constants
from src.plot_functions.plot_agentEstimator import AgentEstimatorPloter
from src.plot_functions.plot_controller import ControllerPlot, plot_scenario, plot_scenario_last
from src.plot_functions.plot_targetEstimator import Analyser_Target_TargetEstimator_FormatCSV
import matplotlib.pyplot as plt
import numpy as np

constants.ResultsPath.folder = "../../to_share"
constants.ResultsPath.name_simulation = "chapitre1-use_case"


#constants.ResultsPath.folder = "../../results"
#constants.ResultsPath.name_simulation = "Simple_map"

target_ploter = analyser_simulated_data = Analyser_Target_TargetEstimator_FormatCSV("",
                                                                        constants.ResultsPath.SAVE_LOAD_DATA_REFERENCE,
                                                                        constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER)

user_plotter = Analyser_Target_TargetEstimator_FormatCSV(100, constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_AGENT,
                                                               constants.ResultsPath.SAVE_LOAD_PLOT_MEMORY_AGENT)

controller_ploter_0 = ControllerPlot(0)
controller_ploter_1 = ControllerPlot(1)

fig = plt.figure(figsize=(12, 8),tight_layout = True)
ax = fig.add_subplot(1, 1, 1)
colors = ["red","red","black"]

plot_scenario_last(fig,ax,controller_ploter_0.data)
plot_scenario_last(fig,ax,controller_ploter_1.data)

for element,color in zip(target_ploter.simulated_data_sort_by_target,colors):
    sc = ax.scatter(element.data_list[7], element.data_list[8], c= np.array(element.data_list[0]), s=500, cmap="Spectral",
                     alpha=0.8)
    ax.scatter(element.data_list[7], element.data_list[8], marker='x',color=color, edgecolors='gold', alpha=0.9,s = 100)

colors = colors[2:]
for element,color in zip(user_plotter.data_sort_by_target,colors):
        ax.scatter(element.data_list[7], element.data_list[8],  marker='o',color=color, edgecolors='yellow', alpha=0.8,s = 100)
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


fig1 = plt.figure(figsize=(12, 8),tight_layout = True)
ax1 = fig1.add_subplot(1, 1, 1)
colors = ["black","black","black"]

plot_scenario_last(fig1,ax1,controller_ploter_0.data)
plot_scenario_last(fig1,ax1,controller_ploter_1.data)

for element,color in zip(target_ploter.simulated_data_sort_by_target,colors):
    ax1.scatter(element.data_list[7], element.data_list[8], marker='x',color=color, edgecolors='gold', alpha=0.9)

colors = colors[2:]
for element,color in zip(user_plotter.data_sort_by_target,colors):
       sc1 = ax1.scatter(element.data_list[7], element.data_list[8], c= np.array(element.data_list[2]), s=500, cmap="PRGn",alpha=0.8)
       ax1.scatter(element.data_list[7], element.data_list[8],  marker='o',color=color, edgecolors='gold', alpha=0.8,s = 100)

cb=fig1.colorbar(sc1, ax=ax1)
cb.ax.tick_params(labelsize=15)
cb.ax.set_xlabel("time [s]", fontsize=20)
ax1.xaxis.set_tick_params(labelsize=20)
ax1.yaxis.set_tick_params(labelsize=20)
ax1.set_xlabel("x [m]", fontsize=20)
ax1.set_ylabel("y [m]", fontsize=20)
ax1.set_title("", fontsize=25, fontweight='bold')
ax1.grid(True)
ax1.set_xbound(-1,11)
ax1.set_ybound(-1,11)


fig2 = plt.figure(figsize=(12, 8),tight_layout = True)
ax2 = fig2.add_subplot(1, 1, 1)
colors = ["black"]
for element,color in zip(user_plotter.data_sort_by_target,colors):
        ax2.scatter(element.data_list[1], np.array(element.data_list[2]),  marker='o',color=color, edgecolors='gold', alpha=0.8,s = 100)

ax2.legend(["target_2"],loc=1, fontsize=25)
ax2.set_yticks([0,1])
ax2.set_yticklabels(["agent 0","agent 1"],rotation = 30)
ax2.xaxis.set_tick_params(labelsize=20)
ax2.yaxis.set_tick_params(labelsize=20)
ax2.set_xlabel("time [s]", fontsize=25)
ax2.set_ylabel("agent's id", fontsize=25)
ax2.grid(True)
ax2.set_xbound(0,10)



fig3 = plt.figure(figsize=(12, 8),tight_layout = True)
ax3 = fig3.add_subplot(1, 1, 1)
ax3.scatter(0, 0, marker='x', color='red', edgecolors='gold',s = 100)
ax3.scatter(0, 0, marker='x', color='black', edgecolors='gold',s = 100)
ax3.scatter(0, 0, marker='o', color='black', edgecolors='gold',s = 100)
ax3.scatter(0, 0, marker='D', s=100, c='gold', edgecolors='black')
ax3.legend(["fix targets", "generated target 2's position","filtered target 2's position","camera's positions"], fontsize=20,loc=3)


fig.savefig(constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER + "-- target")
fig1.savefig(constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER + "-- target-time")
fig3.savefig(constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER + "-- time")
fig3.savefig(constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER + "-- legend")

plt.show()

