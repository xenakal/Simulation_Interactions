import numpy as np
from my_utils.interpolation import*
from plot_functions.plot_toolbox import *

def error_squared_discrete(data_ref_list,data_mes_list):

    "Data ref > Data_mes"
    points_ref_list = PointsList()
    points_ref_filter_list = PointsList()
    points_mes_list = PointsList()
    "considering the datalist are from TargetEstimator"
    (x_ref,y_ref,t_ref)=points_ref_list.add_sort_fill(data_ref_list[6], data_ref_list[7],data_ref_list[0])
    points_mes_list.add_sort_fill(data_mes_list[6],data_mes_list[7],data_mes_list[0])
    points_mes_list.del_same_time()
    (x_mes, y_mes, t_mes) = points_mes_list.fill_vectors()


    for point_ref in points_ref_list.points:
        if point_ref in points_mes_list.points:
            points_ref_filter_list.add_point(point_ref)


    (x_ref,y_ref,t_ref) = points_ref_filter_list.fill_vectors()
    error_squared_x = error_squared_list(x_ref, x_mes)
    error_squared_y = error_squared_list(y_ref, y_mes)
    error_squared = error_squared_x_y_list(x_ref, y_ref, x_mes, y_mes)
    plot_error_square(t_ref,x_ref,y_ref,x_mes,y_mes)


def error_squared_with_interpolation(data_ref_list,data_mes_list):

    "Data ref > Data_mes"
    points_ref_list = PointsList()
    points_ref_filter_list = PointsList()
    points_mes_list = PointsList()
    "considering the datalist are from TargetEstimator"
    (x_ref,y_ref,t_ref)=points_ref_list.add_sort_fill(data_ref_list[6], data_ref_list[7],data_ref_list[0])
    (x_mes,y_mes,t_mes)=points_mes_list.add_sort_fill(data_mes_list[6],data_mes_list[7],data_mes_list[0])

    for point_ref in points_ref_list.points:
        if point_ref.time >= points_mes_list.points[0].time and point_ref.time <= points_mes_list.points[-1].time :
            points_ref_filter_list.add_point(point_ref)

    (x_ref,y_ref,t_ref) = points_ref_filter_list.fill_vectors()

    interpolation_ref = InterpolationLine(x_ref,y_ref,t_ref)
    interpolation_mes = InterpolationLine(x_mes,y_mes,t_ref)

    res_ref = interpolation_ref.spline_approximation_3D()
    res_mes =interpolation_mes.spline_approximation_3D()
    (x_ref,y_ref,t_ref) = res_ref[1]
    (x_mes, y_mes,t_mes) = res_mes[1]

    error_squared_x = error_squared_list(x_ref,x_mes)
    error_squared_y = error_squared_list(y_ref,y_mes)
    error_squared = error_squared_x_y_list(x_ref,y_ref,x_mes,y_mes)

    plot_error_square(t_ref, x_ref, y_ref, x_mes, y_mes)


def error_squared_x_y_list(x_ref,y_ref,x_mes,y_mes):
    error_squared_x = error_squared_list(x_ref,x_mes)
    error_squared_Y = error_squared_list(y_ref,y_mes)
    return np.sqrt(np.square(error_squared_x)+np.square(error_squared_Y))

def error_squared_list(list_ref,list_mes):
    np_ref = np.array(list_ref)
    np_mes = np.array(list_mes)
    return np.square(np_ref-np_mes)

def plot_error_square(t_ref,x_ref,y_ref,x_mes,y_mes):

    fig = plt.figure(figsize=(12, 8), tight_layout=True)

    ax =  fig.add_subplot(3,2,(1,3))
    ax1 = fig.add_subplot(3,2,(5,6))
    ax2 = fig.add_subplot(3,2,2)
    ax3 = fig.add_subplot(3,2,4)

    error_squared_x = error_squared_list(x_ref, x_mes)
    error_squared_y = error_squared_list(y_ref, y_mes)
    error_squared = error_squared_x_y_list(x_ref, y_ref, x_mes, y_mes)

    mean_error_squared_x = np.mean(error_squared_x)
    mean_error_squared_y = np.mean(error_squared_y)
    mean_error_squared_x_y = np.mean(error_squared)

    var__error_squared_x = np.var(error_squared_x)
    var__error_squared_y = np.var(error_squared_y)
    var__error_squared_x_y = np.var(error_squared)


    sc = ax.scatter(x_ref, y_ref,s = 100, c=t_ref,cmap="Spectral", alpha=0.4)
    plot_graph_time_x(ax, x_ref,y_ref, "Trajectory", "x []", "y []",
                      curve_label="interpolation_ref")
    plot_graph_x_y(ax, x_mes,y_mes, "Trajectory", "x []", "y []",
                      curve_label="interpolation_mes")
    plot_graph_time_x(ax1,t_ref,error_squared, "squared error norm  x-y", "time []", "[^2]", curve_label="t_value")
    plot_graph_time_x(ax2, t_ref, error_squared_x, "squared error norm  x", "time []", "[^2]", curve_label="t_value")
    plot_graph_time_x(ax3, t_ref, error_squared_y, "squared norm  y", "time []", "[^2]", curve_label= "t_value")

    plot_graph_time_x(ax1, t_ref, mean_error_squared_x_y*np.ones(np.size(t_ref)), "squared error norm  x-y", "time []", "[^2]",
                      curve_label="mean")
    plot_graph_time_x(ax2, t_ref, mean_error_squared_x*np.ones(np.size(t_ref)), "squared error norm  x", "time []", "[^2]",
                      curve_label="mean")
    plot_graph_time_x(ax3, t_ref, mean_error_squared_y*np.ones(np.size(t_ref)), "squared norm  y", "time []", "[^2]", curve_label="mean")

    (yb, yh) = ax1.get_ylim()
    ax1.text(0, yh + 5, "mean error = %.2f" %(np.sqrt(mean_error_squared_x_y)), fontweight='bold', fontsize=10)

    (yb, yh) = ax2.get_ylim()
    ax2.text(0, yb - 15, "mean error = %.2f"%(np.sqrt(mean_error_squared_x)), fontweight='bold', fontsize=10)

    (yb, yh) = ax3.get_ylim()
    ax3.text(0, yb - 15, "mean error = %.2f" %(np.sqrt(mean_error_squared_y)), fontweight='bold', fontsize=10)

    fig.colorbar(sc, ax=ax)
    fig.show()