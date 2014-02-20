"""
Python wrapper for the HYP primitive of BRL-CAD.
"""

from base import Primitive
from brlcad.vmath import Vector
import numpy as np


class Hyperboloid(Primitive):

    def __init__(self, name, base=(0, 0, 0), height=(0, 0, 1), a_vec=(0, 1, 0),
                 b_mag=0.5, base_neck_ratio=0.2, copy=False):
        Primitive.__init__(self, name=name)
        self.base = Vector(base, copy=copy)
        self.height = Vector(height, copy=copy)
        self.a_vec = Vector(a_vec, copy=copy)
        self.b_mag = b_mag
        self.base_neck_ratio = base_neck_ratio

    def __repr__(self):
        return "{}({}, base={}, height={}, a_vec={}, b_mag={}, base_neck_ratio={})".format(
            self.__class__.__name__, self.name, repr(self.base), repr(self.height),
            repr(self.a_vec), self.b_mag, self.base_neck_ratio
        )

    def update_params(self, params):
        params.update({
            "base": self.base,
            "height": self.height,
            "a_vec": self.a_vec,
            "b_mag": self.b_mag,
            "base_neck_ratio": self.base_neck_ratio,
        })

    def copy(self):
        return Hyperboloid(self.name, self.base, self.height, self.a_vec, self.b_mag, self.base_neck_ratio, copy=True)

    def is_same(self, other):
        if not np.allclose((self.b_mag, self.base_neck_ratio), (other.b_mag, other.base_neck_ratio)):
            return False
        return all(map(Vector.is_same, (self.base, self.height, self.a_vec), (other.base, other.height, other.a_vec)))

    @staticmethod
    def from_wdb(name, data):
        return Hyperboloid(
            name=name,
            base=data.hyp_Vi,
            height=data.hyp_Hi,
            a_vec=data.hyp_A,
            b_mag=data.hyp_b,
            base_neck_ratio=data.hyp_bnr,
        )
