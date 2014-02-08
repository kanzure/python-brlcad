"""
Python wrapper for the ARB8 primitive of BRL-CAD.
This covers in fact the whole ARB4-ARB8 series of primitives, as all those are
saved internally as ARB8.
"""

from base import Primitive
from brlcad.vmath import Vector
import numpy as np


class ARB8(Primitive):

    def __init__(self, type_id, db_internal, directory, data):
        Primitive.__init__(self, type_id, db_internal, directory, data)
        self.point_mat = np.ctypeslib.as_array(data.pt)
        self.points = [Vector(row, copy=False) for row in self.point_mat]

    def __repr__(self):
        return "ARB8({0}, {1})".format(self.name, self.point_mat)
