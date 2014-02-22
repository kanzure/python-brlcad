"""
Python wrapper for the Particle primitive of BRL-CAD.
"""

from base import Primitive
from brlcad.vmath import Vector
import numpy as np


class Particle(Primitive):

    def __init__(self, name, base=(0, 0, 0), height=(0, 0, 1), r_base=0.5, r_end=0.2, copy=False):
        Primitive.__init__(self, name=name)
        self.base = Vector(base, copy=copy)
        self.height = Vector(height, copy=copy)
        self.r_base = r_base
        self.r_end = r_end

    def __repr__(self):
        return "{}({}, base={}, height={}, r_base={}, r_end={})".format(
            self.__class__.__name__, self.name, repr(self.base), repr(self.height), self.r_base, self.r_end
        )

    def update_params(self, params):
        params.update({
            "base": self.base,
            "height": self.height,
            "r_base": self.r_base,
            "r_end": self.r_end,
        })

    def copy(self):
        return Particle(self.name, base=self.base, height=self.height, r_base=self.r_base, r_end=self.r_end, copy=True)

    def has_same_data(self, other):
        if not np.allclose((self.r_base, self.r_end), (other.r_base, other.r_end)):
            return False
        return all(map(Vector.is_same, (self.base, self.height), (other.base, other.height)))

    @staticmethod
    def from_wdb(name, data):
        return Particle(
            name=name,
            base=data.part_V,
            height=data.part_H,
            r_base=data.part_vrad,
            r_end=data.part_hrad,
        )
