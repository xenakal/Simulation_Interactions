import numpy as np

from src.my_utils.my_math.interpolation import PointsList, InterpolationLine

X_INDEX = 7
Y_INDEX = 8
TIME_TO_COMPARE = 0


def error_squared_discrete(data_ref_list, data_mes_list, remove_outliers=False):
    (t_ref, x_ref, y_ref, t_mes, x_mes, y_mes) = get_comparable_data_btw_reference_mesure(data_ref_list, data_mes_list)
    error_squared_x = error_squared_list(x_ref, x_mes)
    error_squared_y = error_squared_list(y_ref, y_mes)
    error_squared = error_squared_x_y_list(x_ref, y_ref, x_mes, y_mes)
    if remove_outliers:
        number_outliers_to_remove = int(len(data_mes_list)/20)
        while number_outliers_to_remove > 0:
            idx_max_mse = error_squared.index(min(error_squared))
            del(error_squared[idx_max_mse])
            del (error_squared_x[idx_max_mse])
            del (error_squared_y[idx_max_mse])
            del (error_squared[idx_max_mse])
            del (error_squared_x[idx_max_mse])
            del (error_squared_y[idx_max_mse])
            del (error_squared_x[idx_max_mse])
            del (error_squared_y[idx_max_mse])
    return t_ref, x_ref, y_ref, x_mes, y_mes, error_squared_x, error_squared_y, error_squared


def error_squared_with_interpolation(data_ref_list, data_mes_list):
    """Data ref > Data_mes"""
    points_ref_list = PointsList()
    points_ref_filter_list = PointsList()
    points_mes_list = PointsList()
    """considering the datalist are from TargetEstimator"""
    (x_ref, y_ref, t_ref) = points_ref_list.add_sort_fill(data_ref_list[X_INDEX], data_ref_list[Y_INDEX],
                                                          data_ref_list[TIME_TO_COMPARE])
    (x_mes, y_mes, t_mes) = points_mes_list.add_sort_fill(data_mes_list[X_INDEX], data_mes_list[Y_INDEX],
                                                          data_mes_list[TIME_TO_COMPARE])

    for point_ref in points_ref_list.points:
        if points_mes_list.points[0].time <= point_ref.time <= points_mes_list.points[-1].time:
            points_ref_filter_list.add_point(point_ref)

    (x_ref, y_ref, t_ref) = points_ref_filter_list.fill_vectors()

    interpolation_ref = InterpolationLine(x_ref, y_ref, t_ref)
    interpolation_mes = InterpolationLine(x_mes, y_mes, t_ref)

    res_ref = interpolation_ref.spline_approximation_3D()
    res_mes = interpolation_mes.spline_approximation_3D()
    (x_ref, y_ref, t_ref) = res_ref[1]
    (x_mes, y_mes, t_mes) = res_mes[1]

    error_squared_x = error_squared_list(x_ref, x_mes)
    error_squared_y = error_squared_list(y_ref, y_mes)
    error_squared = error_squared_x_y_list(x_ref, y_ref, x_mes, y_mes)
    return (t_ref, x_ref, y_ref, x_mes, y_mes)


def get_comparable_data_btw_reference_mesure(data_ref_list, data_mes_list):
    """Data ref > Data_mes"""
    points_ref_list = PointsList()
    points_ref_filter_list = PointsList()
    points_mes_list = PointsList()
    points_mes_filter_list = PointsList()

    """considering the datalist are from TargetEstimator"""
    points_ref_list.add_sort_fill(data_ref_list[X_INDEX], data_ref_list[Y_INDEX], data_ref_list[TIME_TO_COMPARE])
    points_ref_list.del_same_time()
    points_mes_list.add_sort_fill(data_mes_list[X_INDEX], data_mes_list[Y_INDEX], data_mes_list[TIME_TO_COMPARE])
    points_mes_list.del_same_time()

    for point_ref in points_ref_list.points:
        if point_ref in points_mes_list.points:
            points_ref_filter_list.add_point(point_ref)

    for point_mes in points_mes_list.points:
        if point_mes in points_ref_list.points:
            points_mes_filter_list.add_point(point_mes)

    (x_ref, y_ref, t_ref) = points_ref_filter_list.fill_vectors()
    (x_mes, y_mes, t_mes) = points_mes_filter_list.fill_vectors()

    return t_ref, x_ref, y_ref, t_mes, x_mes, y_mes


def error_squared_x_y_list(x_ref, y_ref, x_mes, y_mes):
    error_squared_x = error_squared_list(x_ref, x_mes)
    error_squared_Y = error_squared_list(y_ref, y_mes)
    return np.sqrt(np.square(error_squared_x) + np.square(error_squared_Y))


def error_squared_list(list_ref, list_mes):
    np_ref = np.array(list_ref)
    np_mes = np.array(list_mes)
    return np.square(np_ref - np_mes)
