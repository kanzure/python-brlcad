"""
Python wrappers for the Grip primitives of BRL-CAD.
"""
from base import Primitive
from brlcad.vmath import Vector
import brlcad.ctypes_adaptors as cta


class Grip(Primitive):

    def __init__(self, name, center=(0, 0, 0), normal=(1, 0, 0), magnitude=1, copy=False):
        Primitive.__init__(self, name=name)
        self.center = Vector(center, copy=copy)
        self.normal = Vector(normal, copy=copy)
        self.magnitude = magnitude

    def __repr__(self):
        result = "{}({}, center={}, normal={}, magnitude={})"
        return result.format(
            self.__class__.__name__, self.name, self.center, self.normal, self.magnitude
        )

    def update_params(self, params):
        params.update({
            "center": self.center,
            "normal": self.normal,
            "magnitude": self.magnitude
        })

    def copy(self):
        return Grip(self.name, self.center, self.normal, self.magnitude, copy=True)

    def has_same_data(self, other):
        return self.center.is_same(other.center) and \
               self.normal.is_same(other.normal) and \
               self.magnitude == other.magnitude


    @staticmethod
    def from_wdb(name, data):
        return Grip(
            name=name,
            center=data.center,
            normal=data.normal,
            magnitude=data.mag
        )
