import math
import matplotlib.pyplot as plt
import numpy as np
import re
from src import constants

def load_controller_file(agent_id):
    fichier = open(constants.ResultsPath.LOG_AGENT + "Controller -  agent " + str(agent_id) + " .txt", "r")

    lines = fichier.readlines()
    fichier.close()

    data = [[],[],[],[],[],[],[],[],[],[],[],[],[]]

    for line in lines:
        line = line.replace("\n", "")
        line = line.replace(" ", "")

        if line[0] == "#" or line =="" or line == None:
            pass
        else:
            line = line[40:]
            values = re.split(",", line)
            for n,value in enumerate(values):
                number = float(re.split(":", value)[1])
                data[n].append(number)

    return data

def plot_scenario_last(fig,ax,data):
    #sc = ax.scatter(data[5][-1], data[6][-1], c=data[0][-1], s=1000, cmap="Spectral",alpha=0.3)
    sc = ax.scatter(data[5][-1], data[6][-1], marker='*', s=200, c='orangered', edgecolors='black')
    sc = ax.scatter(data[1][-1], data[2][-1], marker='D', s=100, c='gold', edgecolors='black')

    ax.arrow(data[1][-1], data[2][-1], 0.5 * np.cos(data[3][-1]), 0.5 * np.sin(data[3][-1]), head_width=0.15, head_length=0.3,
                 fc='black', ec='black')

    #ax.legend(["time", "targeted", "measured","alpha"], fontsize=20,loc=3)

def plot_scenario(fig,ax,data):
    sc = ax.scatter(data[5] + data[1], data[6] + data[2], c=data[0] + data[0], s=1000, cmap="Spectral",
                    alpha=0.3)
    #fig.colorbar(sc, ax=ax)
    sc = ax.scatter(data[5], data[6], marker='*', s=200, c='orangered', edgecolors='black')
    sc = ax.scatter(data[1], data[2], marker='D', s=100, c='gold', edgecolors='black')

    for n, angle in enumerate(data[3]):
        ax.arrow(data[1][n], data[2][n], 0.5 * np.cos(angle), 0.5 * np.sin(angle), head_width=0.15, head_length=0.3,
                 fc='black', ec='black')
    #ax.legend(["time", "targeted", "measured","alpha"], fontsize=20,loc=3)


def plot(data):
    fig = plt.figure(figsize=(18, 12),tight_layout = True)
    #fig.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
    ax = fig.add_subplot(4, 2, (1,5))
    ax1 = fig.add_subplot(4, 2, 2)
    ax2 = fig.add_subplot(4, 2, 4)
    ax3 = fig.add_subplot(4, 2, 6)
    ax4 = fig.add_subplot(4, 2, (7,8))

    plot_scenario(fig,ax,data)

    sc1 = ax1.scatter(data[0], data[5], marker='*', s=100, c='gold', edgecolors='red')
    sc1 = ax1.scatter(data[0], data[1],marker='D', s=25, c='gold', edgecolors='red',alpha=0.5)
    ax1.legend(["x_targeted", "x_measured"],fontsize=10)
    ax1.set_title("x-coordinate in terms of time", fontsize=20, fontweight='bold')
    ax1.set_xlabel("time [s]", fontsize=20)
    ax1.set_ylabel("x [m]", fontsize=20)

    sc2 = ax2.scatter(data[0], data[6], marker='*', s=200, c='gold', edgecolors='blue')
    sc2 = ax2.scatter(data[0], data[2], marker='D', s=25, c='gold', edgecolors='blue',alpha=0.5)
    ax2.legend(["y_targeted", "y_measured"],fontsize=10)
    ax2.set_title("y-coordinate in terms of time", fontsize=20, fontweight='bold')
    ax2.set_xlabel("time [s]", fontsize=20)
    ax2.set_ylabel("y [m]", fontsize=20)

    sc3 = ax3.scatter(data[0], np.array(data[7])*180/math.pi, marker='*', s=100, c='gold', edgecolors='green')
    sc3 = ax3.scatter(data[0], np.array(data[3])*180/math.pi, marker='D', s=25, c='gold', edgecolors='green',alpha=0.5)
    ax3.legend(["alpha_targeted", "alpha_measured"],fontsize=10)
    ax3.set_title("alpha-coordinate in terms of time",fontsize=20,fontweight='bold')
    ax3.set_xlabel("time [s]", fontsize=20)
    ax3.set_ylabel("alpha [°]", fontsize=20)

    sc4 = ax4.plot(data[0], np.array(data[9])*100, '.',color ='red')
    sc4 = ax4.plot(data[0], np.array(data[10])*100, '.',color ='blue')
    sc4 = ax4.plot(data[0], np.array(data[11])*100, '.',color='green')
    #sc4 = ax4.plot(data[0], np.array(data[12])*100, '.', color='gold')
    ax4.set_title("controller command in terms of time", fontsize=20, fontweight='bold')
    ax4.set_xlabel("time [s]", fontsize=20)
    ax4.set_ylabel("command [%]", fontsize=20)
    ax4.legend(["x_command","y_command","alpha_command"],fontsize=10)


    ax.xaxis.set_tick_params(labelsize=15)
    ax.yaxis.set_tick_params(labelsize=15)
    ax1.xaxis.set_tick_params(labelsize=15)
    ax1.yaxis.set_tick_params(labelsize=15)
    ax2.xaxis.set_tick_params(labelsize=15)
    ax2.yaxis.set_tick_params(labelsize=15)
    ax3.xaxis.set_tick_params(labelsize=15)
    ax3.yaxis.set_tick_params(labelsize=15)
    ax4.xaxis.set_tick_params(labelsize=15)
    ax4.yaxis.set_tick_params(labelsize=15)
    ax.set_xlabel("x [m]", fontsize=20)
    ax.set_ylabel("y [m]", fontsize=20)
    ax.set_title("", fontsize=25, fontweight='bold')
    #ax.legend(["targets positions"], loc=2, fontsize=20)
    ax.grid(True)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax.set_xbound(-1, 11)
    ax.set_ybound(-1, 11)
    #fig.savefig("test")
    plt.show()


class ControllerPlot:
    def __init__(self,agent_id):
        self.data = load_controller_file(agent_id)
        self.id = agent_id


    def plot(self):
        plot(self.data)

if __name__ == '__main__':
    constants.ResultsPath.folder = "../../results"
    constants.ResultsPath.name_simulation = "Super_use-case_fix"
    plot_creator = ControllerPlot(0)
    plot_creator.plot()
