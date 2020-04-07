import math
import numpy


def distance_btw_two_point(x1, y1, x2, y2):
    return math.pow(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2), 0.5)


class Line:
    def __init__(self, x, y, x1, y1):
        self.xa = x
        self.ya = y
        self.tol = 0.0000000001

        '''Taking verticality into account'''
        if math.fabs(x - x1) < self.tol:
            self.m = None
        else:
            self.m = (y - y1) / (x - x1)

    def compute_x(self, y):
        if self.m is None:
            return self.xa
        else:
            return (y - self.ya) / self.m

    def compute_y(self,x):
        """
            :param
                - x
            :return
                - Compute the y coordinate for the value of x
        """
        if self.m is None:
            return self.ya
        else:
            return self.ya+x*self.m

    def find_line_perp(self, x, y):
        """
        :param
            - x,y coordinate from the point threw which the line should pass
        :return
            - return a Line, perpendicular to self
        """

        if self.m is None:
            """if line is vertical"""
            return Line(x, y, x + 1, y)
        elif math.fabs(self.m) < self.tol:
            """if line is horizontal"""
            return Line(x, y, x , y)
        else:
            """Every other line"""
            y1 = (-1 / self.m) + y
            return Line(x, y, x + 1, y1)

    def find_intersection_btw_two_line(self, line):
        """
          :param
              - Line object
          :return
              - return x,y intersection of the two line.
        """
        if self.m == line.m:
            "Line parallel => no intersection"
            xi = None
            yi = None

        elif self.m is None:
            "self is vertical"
            xi = self.xa
            yi = line.compute_y(xi)

        elif line.m is None:
            "line is vertical"
            xi = line.xa
            yi = self.compute_y(xi)

        elif math.fabs(self.m) < self.tol:
            """self is horizontal"""
            yi = self.xa
            xi = line.compute_y(yi)

        elif math.fabs(self.m) < self.tol:
            """line is horizontal"""
            yi = line.ya
            xi = line.compute_y(yi)

        else:
            """Every other line"""
            xi = (line.m * line.xa - self.m * self.xa - line.ya + self.ya) / (line.m - self.m)
            yi = self.m * (xi - self.xa) + self.ya

        return xi, yi


    def find_intersection_btw_line_circle(self, r, xc, yc):
        """
            :param
                - xc,yc is the center of the circle
                - r is the radius of the circle
            :return
                - return x1,y1 and x2,y2 intersection a circle and self.
                if x1=y1=x2=y2 then there is no intersection

        """
        if r == 0:
            x1 = xc
            y1 = yc
            x2 = xc
            y2 = yc

        elif self.m is None:
            x1 = self.xa
            y1 = math.pow((r * r - (self.xa - xc) * (self.xa - xc)), 0.5) + yc
            x2 = self.xa
            y2 = -math.pow((r * r - (self.xa - xc) * (self.xa - xc)), 0.5) + yc
        else:
            m = self.m
            xd = self.xa
            yd = self.ya

            a = 1 + m * m
            b = -2 * xc - 2 * m * m * xd + 2 * m * yd - 2 * m * yc
            c = xc * xc + m * m * xd * xd - 2 * m * yd * xd + yd * yd + 2 * m * yc * xd - 2 * yc * yd + yc * yc - r * r

            delta = b * b - 4 * a * c
            try:
                x1 = (-b - math.pow(delta, 0.5)) / (2 * a)
                x2 = (-b + math.pow(delta, 0.5)) / (2 * a)
                y1 = m * (x1 - self.xa) + self.ya
                y2 = m * (x2 - self.xa) + self.ya
            except ValueError:
                x1 = 0
                x2 = 0
                y1 = 0
                y2 = 0
                print("Class Line Error")

        return numpy.array([x1, y1, x2, y2])
