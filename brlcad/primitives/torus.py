"""
Python wrappers for the TOR and ETO primitives of BRL-CAD.
"""

from base import Primitive
from brlcad.vmath import Vector
import numpy as np


class Torus(Primitive):

    def __init__(self, name, center=(0, 0, 0), n=(0, 0, 1), r_revolution=1, r_cross=0.2, copy=False):
        Primitive.__init__(self, name=name)
        self.center = Vector(center, copy=copy)
        self.n = Vector(n, copy=copy)
        self.r_revolution = r_revolution
        self.r_cross = r_cross

    def __repr__(self):
        return "{}({}, center={}, n={}, r_revolution={}, r_cross={})".format(
            self.__class__.__name__, self.name, repr(self.center), repr(self.n), self.r_revolution, self.r_cross
        )

    def update_params(self, params):
        params.update({
            "center": self.center,
            "n": self.n,
            "r_revolution": self.r_revolution,
            "r_cross": self.r_cross,
        })

    def copy(self):
        return Torus(self.name, center=self.center, n=self.n,
                     r_revolution=self.r_revolution, r_cross=self.r_cross, copy=True)

    def has_same_data(self, other):
        if not np.allclose((self.r_revolution, self.r_cross), (other.r_revolution, other.r_cross)):
            return False
        return all(map(Vector.is_same, (self.center, self.n), (other.center, other.n)))

    @staticmethod
    def from_wdb(name, data):
        return Torus(
            name=name,
            center=data.v,
            n=data.h,
            r_revolution=data.r_a,
            r_cross=data.r_h,
        )


class ETO(Primitive):

    def __init__(self, name, center=(0, 0, 0), n=(0, 0, 1),
                 s_major=(0, 0.5, 0.5), r_revolution=1, r_minor=0.2, copy=False):
        Primitive.__init__(self, name=name)
        self.center = Vector(center, copy=copy)
        self.n = Vector(n, copy=copy)
        self.s_major = Vector(s_major, copy=copy)
        self.r_revolution = r_revolution
        self.r_minor = r_minor

    def __repr__(self):
        return "{}({}, center={}, n={}, s_major={}, r_revolution={}, r_minor={})".format(
            self.__class__.__name__, self.name, repr(self.center), repr(self.n),
            repr(self.s_major), self.r_revolution, self.r_minor
        )

    def update_params(self, params):
        params.update({
            "center": self.center,
            "n": self.n,
            "s_major": self.s_major,
            "r_revolution": self.r_revolution,
            "r_minor": self.r_minor,
        })

    def copy(self):
        return ETO(self.name, center=self.center, n=self.n, s_major=self.s_major,
                   r_revolution=self.r_revolution, r_minor=self.r_minor, copy=True)

    def has_same_data(self, other):
        if not np.allclose((self.r_revolution, self.r_minor), (other.r_revolution, other.r_minor)):
            return False
        return all(map(Vector.is_same, (self.center, self.n, self.s_major), (other.center, other.n, other.s_major)))

    @staticmethod
    def from_wdb(name, data):
        return ETO(
            name=name,
            center=data.eto_V,
            n=data.eto_N,
            s_major=data.eto_C,
            r_revolution=data.eto_r,
            r_minor=data.eto_rd,
        )
