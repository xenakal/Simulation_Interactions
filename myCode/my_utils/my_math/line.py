import math
import numpy

def distance_btw_two_point(x1, y1, x2, y2):
    return math.pow(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2), 0.5)

"""
Class line, represent a line in a 2D plane
:init
    - x,y  : coordinate from point 1 
    - x1,y1 :coordinate from point 2
    
:param 
    x,y: point threw which the line goes
    tol: slope smaller than tol is consider to be 0 
"""
class Line:
    def __init__(self, x, y, x1, y1):
        self.x = x
        self.y = y
        self.tol = 0.0000000001

        '''Taking verticality into account'''
        if math.fabs(x - x1) < self.tol :
            self.m = 1
            self.vertical = 1
        else:
            self.m = (y - y1) / (x - x1)
            self.vertical = 0

    """
    :param
        -None
    :return 
        - Slope on  radian 
    """
    def getSlope(self):
        return numpy.array([self.m,self.vertical])

    """
    :param
        - x,y coordinate from the point threw which the line should pass
    :return 
        - return a Line, perpendicular to self
    """
    def linePerp(self, x, y):
        if math.fabs(self.m) < self.tol:
            return Line(x, y, x, y + 1)
        elif self.vertical == 1:
            return Line(x, y, x + 1, y)
        else:
            y1 = (-1 / self.m) + y
            return Line(x, y, x + 1, y1)

    """
      :param
          - Line object
      :return 
          - return x,y intersection of the two line.
      """
    def lineIntersection(self, line):
        if line.m == self.m and self.vertical == 0 and line.vertical == 0:
            return 0
        elif self.vertical == 1 and line.vertical == 1:
            return 0
        elif self.vertical == 1:
            y = line.m * (self.x - line.x) + line.y
            return numpy.array([self.x, y])
        elif line.vertical == 1:
            y = self.m * (line.x - self.x) + self.y
            return numpy.array([line.x, y])
        else:
            x = (line.m * line.x - self.m * self.x - line.y + self.y) / (line.m - self.m)
            y = self.m * (x - self.x) + self.y
            return numpy.array([x, y])

    """
        :param
            - xc,yc is the center of the circle
            - r is the radius of the circle
        :return 
            - return x1,y1 and x2,y2 intersection a circle and self.
            if x1=y1=x2=y2 then there is no intersection
            
    """
    def lineCircleIntersection(self, r, xc, yc):

        if r == 0:
            x1 = xc
            y1 = yc
            x2 = xc
            y2 = yc

        elif self.vertical == 1:
            x1 = self.x
            y1 = math.pow((r * r - (self.x - xc) * (self.x - xc)), 0.5) + yc
            x2 = self.x
            y2 = -math.pow((r * r - (self.x - xc) * (self.x - xc)), 0.5) + yc
        else:
            m = self.m
            xd = self.x
            yd = self.y

            a = 1 + m * m
            b = -2 * xc - 2 * m * m * xd + 2 * m * yd - 2 * m * yc
            c = xc * xc + m * m * xd * xd - 2 * m * yd * xd + yd * yd + 2 * m * yc * xd - 2 * yc * yd + yc * yc - r * r

            delta = b * b - 4 * a * c
            try:
                x1 = (-b - math.pow(delta, 0.5)) / (2 * a)
                x2 = (-b + math.pow(delta, 0.5)) / (2 * a)
                y1 = m * (x1 - self.x) + self.y
                y2 = m * (x2 - self.x) + self.y
            except ValueError:
                x1 = 0
                x2 = 0
                y1 = 0
                y2 = 0
                print("Class Line Error")
                

        return numpy.array([x1, y1, x2, y2])
