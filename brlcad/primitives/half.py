"""
Python wrappers for the HALF primitives of BRL-CAD.
"""
from base import Primitive
from brlcad.vmath import Vector, Plane
import brlcad.ctypes_adaptors as cta


class Half(Primitive):

    def __init__(self, name, norm=(1, 0, 0), d=1.0, plane=None, copy=False):
        Primitive.__init__(self, name=name)
        if plane is not None:
            self.plane = plane
        else:
            self.plane = Plane(Vector(norm), d, copy=copy)

    def __repr__(self):
        result = "{}({}, Plane={})"
        return result.format(
            self.__class__.__name__, self.name, repr(self.plane)
        )

    def update_params(self, params):
        params.update({
            "norm": self.plane.normal,
            "d": self.plane.distance
        })

    def copy(self):
        return Half(self.name, self.plane.normal, self.plane.distance, copy=True)

    def has_same_data(self, other):
        return self.plane.is_same(other.plane)


    @staticmethod
    def from_wdb(name, data):
        plane = cta.plane_from_pointer(data.eqn)
        return Half(
            name=name,
            plane=plane
        )