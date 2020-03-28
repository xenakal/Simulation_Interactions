from matplotlib import cm

import constants
import numpy as np
from plot_functions.plot_targetEstimator import *

"To plot a graph just put the agent id and run"

constants.ResultsPath.folder = "../results"
constants.ResultsPath.name_simulation = "My_new_map"

fig = plt.figure(figsize=(12, 8))
fig.suptitle('test', fontsize=17, fontweight='bold', y=0.98)
fig.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
ax1 = fig.add_subplot(1, 2, 1) # ,projection='3d')
ax2 = fig.add_subplot(1, 2, 2)

cov = np.loadtxt("coverage")
region = np.loadtxt("region")
xv = np.loadtxt("x")
yv = np.loadtxt("y")

sc1 = ax1.scatter(xv, yv, c= np.array(cov), cmap="hot", linewidth=0.01)
sc2 = ax2.scatter(xv, yv, c= np.array(region), cmap="viridis", linewidth=0.01)
fig.colorbar(sc1, ax=ax1)
fig.colorbar(sc2, ax=ax2)
fig.savefig("Static_analysis" ,
            transparent=False)
plt.close(fig)
