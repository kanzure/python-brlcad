"""
Python wrapper for the ARB8 primitive of BRL-CAD.
This covers in fact the whole ARB4-ARB8 series of primitives, as all those are
saved internally as ARB8.
"""

from base import Primitive
import numpy as np


class ARB8(Primitive):

    def __init__(self, type_id, db_internal, directory, data):
        Primitive.__init__(self, type_id=type_id, db_internal=db_internal, directory=directory, data=data)
        self.point_mat = np.ctypeslib.as_array(data.pt)

    def __repr__(self):
        return "ARB8({0}, {1})".format(self.name, self.point_mat)

    def _get_points(self):
        # returns tuple because it should be immutable
        return tuple(self.point_mat.flat)

    points = property(_get_points)

    def update_params(self, params):
        params.update({
            "points": self.points,
        })
