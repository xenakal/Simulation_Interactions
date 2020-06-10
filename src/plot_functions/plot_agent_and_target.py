from src import constants
from src.plot_functions.plot_agentEstimator import AgentEstimatorPloter
from src.plot_functions.plot_controller import ControllerPlot, plot_scenario, plot_scenario_last
from src.plot_functions.plot_targetEstimator import Analyser_Target_TargetEstimator_FormatCSV
import matplotlib.pyplot as plt
import numpy as np

constants.ResultsPath.folder = "../../results"
constants.ResultsPath.name_simulation = "super_use-case_fix"

#agent_ploter = AgentEstimatorPloter(0)
#controller_ploter_0 = ControllerPlot(0)
#controller_ploter_1 = ControllerPlot(1)
#controller_ploter_2 = ControllerPlot(2)


target_ploter = analyser_simulated_data = Analyser_Target_TargetEstimator_FormatCSV("",
                                                                        constants.ResultsPath.SAVE_LOAD_DATA_REFERENCE,
                                                                        constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER)
user_plotter = Analyser_Target_TargetEstimator_FormatCSV(100, constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_AGENT,
                                                               constants.ResultsPath.SAVE_LOAD_PLOT_MEMORY_AGENT)




fig = plt.figure(figsize=(12, 8))
fig.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
ax = fig.add_subplot(1, 1, 1)

#plot_scenario_last(fig,ax,controller_ploter_0.data)
#plot_scenario_last(fig,ax,controller_ploter_1.data)
#plot_scenario_last(fig,ax,controller_ploter_2.data)

colors = ["black","black","blue","red","green","orange"]
for element,color in zip(target_ploter.simulated_data_sort_by_target,colors):
    sc = ax.scatter(element.data_list[7], element.data_list[8], c= np.array(element.data_list[0]), s=500, cmap="Spectral",
                     alpha=0.3)
    sc1 = ax.scatter(element.data_list[7], element.data_list[8], marker='x',color=color, edgecolors='black', alpha=0.7)
#fig.colorbar(sc, ax=ax)

colors = colors[2:]
for element,color in zip(user_plotter.data_sort_by_target,colors):
        print(element.target_id)
        #sc = ax.scatter(element.data_list[7], element.data_list[8], c= np.array(element.data_list[2]), s=500, cmap="PRGn",
        #s                 alpha=0.3)
        sc1 = ax.scatter(element.data_list[7], element.data_list[8],  marker='o',color=color, edgecolors='black', alpha=0.8,s = 100)
fig.colorbar(sc, ax=ax)

ax.xaxis.set_tick_params(labelsize=20)
ax.yaxis.set_tick_params(labelsize=20)
ax.set_xlabel("x [m]", fontsize=20)
ax.set_ylabel("y [m]", fontsize=20)
ax.set_title("", fontsize=25, fontweight='bold')
#ax.legend(["time", "agent_targeted", "agent_measured","target 1","target 2"],loc=2, fontsize=20)
ax.grid(True)
ax.set_xbound(-1,16)
ax.set_ybound(-1,11)

fig1 = plt.figure(figsize=(12, 8))
fig1.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
ax1 = fig1.add_subplot(1, 1, 1)
offset = 0
for element,color in zip(user_plotter.data_sort_by_target,colors):
        print(element.target_id)
        sc1 = ax1.scatter(element.data_list[1], np.array(element.data_list[2])+offset,  marker='o',color=color, edgecolors='black', alpha=0.8,s = 100)
        offset += 0.1
ax1.legend(["target_2", "target_3", "target_4","target_5","target 2"],loc=1, fontsize=25)
#ax1.legend(["target_2"],loc=1, fontsize=25)
ax1.set_yticks([0+offset/2,1+offset/2,2+offset/2])
#ax1.set_yticks([0+offset/2,1+offset/2])
ax1.set_yticklabels(["agent 0","agent 1","agent 2"],rotation = 30)
#ax1.set_yticklabels(["agent 0","agent 1"],rotation = 30)
ax1.xaxis.set_tick_params(labelsize=20)
ax1.yaxis.set_tick_params(labelsize=20)
ax1.set_xlabel("time [s]", fontsize=25)
ax1.set_ylabel("agent's id", fontsize=25)
ax1.set_xbound(0,20)

#fig.colorbar(sc, ax=ax)







plt.show()

