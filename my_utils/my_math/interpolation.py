import numpy as np
import time
import matplotlib.pyplot as plt
from scipy import interpolate

from mpl_toolkits.mplot3d import Axes3D
import math

class InterpolationLine():
    def __init__(self, x, y, z=0):
        self.number_of_point = 25
        if not z == 0:
            "To use 3D plot"
            points = PointsList()
            (self.x, self.y, self.z) = points.add_sort_fill(x, y, z)
        else:
            "Then only use 2D methods"
            self.x = x
            self.y = y

    def sort_data_in_tems_of_time(self):
        points = PointsList()
        points.add_points_list(self.x, self.y, self.z)
        points.sort()
        (self.x, self.y, self.z) = points.fill_vectors()

    def spline_approximation_2D(self):
        tck, u = interpolate.splprep([self.x, self.y], s=100, k=2)
        x_knots, y_knots = interpolate.splev(tck[0], tck)
        u_fine = np.linspace(0, 1, self.number_of_point)
        x_fine, y_fine, = interpolate.splev(u_fine, tck)

        return [(x_knots, y_knots), (x_fine, y_fine)]

    def spline_approximation_3D(self):
        tck, u = interpolate.splprep([self.x, self.y, self.z], s=2, k=3)

        x_knots, y_knots, z_knots = interpolate.splev(tck[0], tck)
        u_fine = np.linspace(0, 1, self.number_of_point)
        x_fine, y_fine, z_fine = interpolate.splev(u_fine, tck)

        return [(x_knots, y_knots, z_knots), (x_fine, y_fine, z_fine)]

    def plot_2D(self):
        res = self.spline_approximation_2D()
        (x_knots, y_knots) = res[0]
        (x_fine, y_fine) = res[1]

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.x, self.y, "x")
        ax.plot(x_knots, y_knots, 'go')
        ax.plot(x_fine, y_fine, 'g')
        fig.show()

    def plot_2D_interpolation_3D(self):
        res = self.spline_approximation_3D()
        (x_knots, y_knots, z_knots) = res[0]
        (x_fine, y_fine, z_fine) = res[1]

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.x, self.y, "x")
        ax.plot(x_knots, y_knots, 'go')
        ax.plot(x_fine, y_fine, 'g')
        fig.show()

    def plot_3D(self):
        res = self.spline_approximation_3D()
        (x_knots, y_knots, z_knots) = res[0]
        (x_fine, y_fine, z_fine) = res[1]

        fig = plt.figure()
        ax3d = fig.add_subplot(111, projection='3d')
        ax3d.plot(x_knots, y_knots, z_knots, 'go')
        ax3d.plot(x_fine, y_fine, z_fine, 'g')
        fig.show()

    def interp_test(self):
        pass


class Point():
    def __init__(self, x, y, time):
        self.x = x
        self.y = y
        self.time = time

    def is_x_y_equal(self, other):
        cdt1 = self.x == other.x
        cdt2 = self.y == other.y
        return cdt1 and cdt2

    def __eq__(self, other):
        return math.fabs(self.time) - other.time < 0.1

    def __lt__(self, other):
        return self.time < other.time

    def __gt__(self, other):
        return self.time > other.time


class PointsList:
    def __init__(self):
        self.points = []

    def add_sort_fill(self, x, y, z):
        self.add_points_list(x, y, z)
        self.sort()
        return self.fill_vectors()

    def add_create_point(self, x, y, z):
        point = Point(x, y, z)
        self.points.append(point)

    def add_point(self, point):
        self.points.append(point)

    def add_points_list(self, x, y, z):
        for n in range(len(x)):
            self.add_create_point(x[n], y[n], z[n])

    def fill_vectors(self):
        x = []
        y = []
        z = []
        for point in self.points:
            x.append(point.x)
            y.append(point.y)
            z.append(point.time)
        return (x, y, z)

    def sort(self):
        self.points.sort()

    def del_point(self, point):
        self.points.remove(point)

    def del_same_time(self):
        new_points = []
        for point in self.points:
            if not point in new_points:
                new_points.append(point)
        self.points = new_points

    def remove_point_with_same_x_y(self):
        points_without_same = []
        for point in self.points:
            points_without_same.append(point)
            for same_point in self.points:
                if same_point.is_x_y_equal(point):
                    self.points.remove(same_point)
        return points_without_same
