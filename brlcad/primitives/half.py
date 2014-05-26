"""
Python wrappers for the HALF primitives of BRL-CAD.
"""
from base import Primitive
from brlcad.vmath import Vector, Transform, Plane
import numpy as np
import brlcad.ctypes_adaptors as cta
import os


class HALF(Primitive):

    def __init__(self, name, norm=(1, 0, 0), d=1.0, copy=False):
        Primitive.__init__(self, name=name)
        self.eqn = Plane(Vector(norm),d,copy)

    def __repr__(self):
        result = "{}({}, Eqn={})"
        return result.format(
            self.__class__.__name__, self.name, repr(self.eqn)
        )

    def update_params(self, params):
        params.update({
            "norm": self.eqn.normal,
            "d": self.eqn.distance
        })

    def copy(self):
        return HALF(self.name, self.eqn.normal, self.eqn.distance, copy=True)

    def has_same_data(self, other):
        return self.eqn.is_same(other.eqn)


    @staticmethod
    def from_wdb(name, data):
        plane = cta.plane_from_pointer(data.eqn)
        return HALF(
            name=name,
            norm=plane.normal,
            d=plane.distance
        )