import numpy as np
import math
from src import constants

X_MIN = 0
X_MAX = constants.ROOM_DIMENSION_X + 1
Y_MIN = 0
Y_MAX = constants.ROOM_DIMENSION_Y
T_MIN = 0
T_MAX = 20


def plot_graph_3D(ax, x, y, z, title="title", x_label="x_axis", y_label="y_axis", z_label="z_label"):
    ax.plot(x, y, z, label='parametric curve')

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


def plot_graph_3D_2D(ax, x, y, z, size, vmin, vmax, title="title", x_label="x_axis", y_label="y_axis",
                     curve_label="name here"):
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=15, fontweight='bold')
    ax.set_xlim(Y_MIN, X_MAX)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.grid(True)

    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    # points = np.array([x, y]).T.reshape(-1, 1, 2)
    # segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # my_norm = plt.Normalize(0, max(z))
    # lc = LineCollection(segments, cmap='viridis', norm=my_norm)

    # cmap = ListedColormap(['r', 'g', 'b'])
    # my_norm = BoundaryNorm([0, 1, 2, 3], cmap.N)
    # lc = LineCollection(segments, cmap=cmap, norm=my_norm)

    # Set the values used for colormapping
    # lc.set_array(z)
    # lc.set_linewidth(2)
    # line = ax.add_collection(lc)

    sc = ax.scatter(x, y, c=z, s=2500 * math.pow(size[0], 2) * math.pi, vmin=vmin, vmax=vmax, cmap="Spectral",
                    alpha=0.4)
    ax.plot(x, y, "x", label=curve_label)
    ax.legend(loc=4)

    return sc


def plot_graph_2D(ax, x, y, title="title", x_label="x_axis", y_label="y_axis", curve_label="name here"):
    x = np.array(x)
    y = np.array(y)
    ax.plot(x, y, "x", label=curve_label)

    ax.grid(True)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=15, fontweight='bold')
    ax.legend(loc=4)


def plot_graph_x_y(ax, x, y, title="title", x_label="x_axis", y_label="y_axis", curve_label="name here"):
    plot_graph_2D(ax, x, y, title=title, x_label=x_label, y_label=y_label, curve_label=curve_label)
    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(Y_MIN, Y_MAX)


def plot_graph_time_x(ax, time, x, title="title", x_label="x_axis", y_label="y_axis", curve_label="name here"):
    plot_graph_2D(ax, time, x, title=title, x_label=x_label, y_label=y_label, curve_label=curve_label)
    ax.set_xlim(T_MIN, T_MAX)
