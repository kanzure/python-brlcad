"""
Python wrapper for the ARB8 primitive of BRL-CAD.
This covers in fact the whole ARB4-ARB8 series of primitives, as all those are
saved internally as ARB8.
"""

from base import Primitive
import numpy as np


class ARB8(Primitive):

    def __init__(self, name, points, copy=False):
        """
        The points parameter is a sequence of 24(=8*3) floats.
        It doesn't matter in what form the floats are organized
        (e.g. sequence of 24 floats, sequence of 8 tuples of each 3 floats)
        the only requirement is that they are 24 in total.
        They will be interpreted as 8 vertexes, each composed of 3 floats
        for the (x, y, z) coordinates.
        The ordering of the vertexes is important, the mapping to the ARB8s
        corners is like this:

              V8                    V7
               +--------------------+
              /:                   /|
             / :                  / |
            /  :                 /  |
         V5/   :              V6/   |
          +--------------------+    |
          |    :               |    |
          |    ;...............|....+
          |   ;V4              |   /V3
          |  ;                 |  /
          | ;                  | /
          |;                   |/
          +--------------------+
          V1                   V2

        To have a consistent ARB8, the vertexes of each face must be coplanar.
        The faces are defined and connected in a specific order, so switching
        2 vertexes will result in wrong shape.
        The faces are numbered to allow access to them
        (again, the order of the points is important):

        F1 = (V1, V2, V3, V4)
        F2 = (V5, V6, V7, V8)
        F3 = (V1, V2, V6, V5)
        F4 = (V2, V3, V7, V6)
        F5 = (V3, V4, V8, V7)
        F6 = (V4, V1, V5, V8)

                            F2
                            |      F5
                   V8       |     /      V7
                    +-------|------------+
                   /:       |   /       /|
                  / :          /       / |
                 /  :                 /  |
              V5/   :              V6/   |
               +--------------------+   -------F4
               |    :               |    |
          F6---|--  ;...............|....+
               |   ;V4              |   /V3
               |  ;                 |  /
               | ;      /           | /
               |;      /    |       |/
               +------/-------------+
               V1    /      |       V2
                    F3      |
                            F1

        This primitive can also represent shapes with 4-7 vertexes,
        by collapsing certain vertexes in one point.
        This constructor will accept any number of points between 4-8,
        and do the necessary mapping of points to collapsed vertexes.
        The exact mapping of the points parameter to vertexes follows
        below separately for each of ARB4-ARB7.

        ARB4

        points = (P1, P2, P3, P4)
        vertexes = (V1=P1, V2=P2, V3=P3, V4=P3, V5=P4, V6=P4, V7=P4, V8=P4)

                           P4(V5,V6,V7,V8)
                            +
                           /|\
                          / | \
                         /  |  \
                        /   |   \
                       /    |   ,x
                      /     |,-'/P3(V3,V4)
                     /    ,-|  /
                    /  ,-'  | /
                   /,-'     |/
                  +---------+
                P1(V1)     P2(V2)

        ARB5

        points = (P1, P2, P3, P4, P5)
        vertexes = (V1=P1, V2=P2, V3=P3, V4=P4, V5=P5, V6=P5, V7=P5, V8=P5)

                        P5(V5,V6,V7,V8)
                          _.-+~.,_
               P4(V4) _.-" ." \   '~.,_  P3(V3)
                    +"---."----\-------"-+
                   /   ."       \       /
                  /  ."          \     /
                 / ."             \   /
                /."                \ /
               +"~~~~~~~~~~~~~~~~~~~+
          P1(V1)                  P2(V2)

        ARB6

        points = (P1, P2, P3, P4, P5, P6)
        vertexes = (V1=P1, V2=P2, V3=P3, V4=P4, V5=P5, V6=P5, V7=P6 V8=P6)

                              P6(V7,V8)
                                  .+
                                ,"/ \
                              ," /   \
                          P5(V5,V6)   ".
                          ,"   +        \
                 P4(V4) ,"   ." \        ". P3(V3)
                      +"---."----\---------+
                     /   ."       \       /
                    /  ."          \     /
                   / ."             \   /
                  /."                \ /
                 +"~~~~~~~~~~~~~~~~~~~+
           P1(V1)                      P2(V2)

        ARB7

        points = (P1, P2, P3, P4, P5, P6, P7)
        vertexes = (V1=P1, V2=P2, V3=P3, V4=P4, V5=P5, V6=P6, V7=P7 V8=P5)

                                            P7(V7)
                                        _,.+
                                   _,.~".'/|
                              _,.-"  .-  / |
                         _,.-"    .-    /  |
            P5(V5,V8),-"'      .-  P6(V6)  |
                 +~~~~~~~~~~~~~~~~~~~~+    |
                 | `.    .-'          |    |
                 |   `,:..............|....+
                 |   ;P4(V4)          |   / P3(V3)
                 |  ;                 |  /
                 | ;                  | /
                 |;                   |/
                 +~~~~~~~~~~~~~~~~~~~~+
                 P1(V1)                P2(V2)

        """
        #TODO: implement conversion for ARB4-ARB7
        # (expand points for the collapsed vertexes)
        Primitive.__init__(self, name=name)
        self.point_mat = np.matrix(points, copy=copy)

    def __repr__(self):
        return "ARB8({0}, {1})".format(self.name, self.point_mat)

    def _get_points(self):
        # returns tuple because it should be immutable
        return tuple(self.point_mat.flat)

    points = property(_get_points)

    def copy(self):
        return ARB8(self.name, self.point_mat, copy=True)

    def has_same_data(self, other):
        return np.allclose(self.point_mat, other.point_mat)

    def update_params(self, params):
        params.update({
            "points": self.points,
        })

    @staticmethod
    def from_wdb(name, data):
        return ARB8(
            name=name,
            points=np.ctypeslib.as_array(data.pt)
        )