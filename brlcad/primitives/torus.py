"""
Python wrapper for the TOR primitive of BRL-CAD.
"""

from base import Primitive
from brlcad.vmath import Vector


class Torus(Primitive):

    def __init__(self, name, center=(0, 0, 0), n=(0, 0, 1), r_revolution=1, r_cross=0.2, copy=False):
        Primitive.__init__(self, name=name)
        self.center = Vector(center, copy=copy)
        self.n = Vector(n, copy=copy)
        self.r_revolution = r_revolution
        self.r_cross = r_cross

    def __repr__(self):
        return "Torus({}, center={}, n={}, r_revolution={}, r_cross={})".format(
            self.name, repr(self.center), repr(self.n), self.r_revolution, self.r_cross
        )

    def update_params(self, params):
        params.update({
            "center": self.center,
            "n": self.n,
            "r_revolution": self.r_revolution,
            "r_cross": self.r_cross,
        })

    @staticmethod
    def from_wdb(name, data):
        return Torus(
            name=name,
            center=data.v,
            n=data.h,
            r_revolution=data.r_a,
            r_cross=data.r_h,
        )
