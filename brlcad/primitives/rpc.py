"""
Python wrappers for the RPC and RHC primitives of BRL-CAD.
"""

from base import Primitive
from brlcad.vmath import Vector
import numpy as np


class RPC(Primitive):

    def __init__(self, name, base=(0, 0, 0), height=(-1, 0, 0), breadth=(0, 0, 1), half_width=0.5, copy=False):
        Primitive.__init__(self, name=name)
        self.base = Vector(base, copy=copy)
        self.height = Vector(height, copy=copy)
        self.breadth = Vector(breadth, copy=copy)
        self.half_width = half_width

    def __repr__(self):
        return "{}({}, base={}, height={}, breadth={}, half_width={})".format(
            self.__class__.__name__, self.name, repr(self.base),
            repr(self.height), repr(self.breadth), self.half_width
        )

    def update_params(self, params):
        params.update({
            "base": self.base,
            "height": self.height,
            "breadth": self.breadth,
            "half_width": self.half_width,
        })

    def copy(self):
        return RPC(self.name, base=self.base, height=self.height,
                   breadth=self.breadth, half_width=self.half_width, copy=True)

    def has_same_data(self, other):
        if not np.allclose(self.half_width, other.half_width):
            return False
        self_vectors = (self.base, self.height, self.breadth)
        other_vectors = (other.base, other.height, other.breadth)
        return all(map(Vector.is_same, self_vectors, other_vectors))

    @staticmethod
    def from_wdb(name, data):
        return RPC(
            name=name,
            base=data.rpc_V,
            height=data.rpc_H,
            breadth=data.rpc_B,
            half_width=data.rpc_r,
        )


class RHC(RPC):

    def __init__(self, name, base=(0, 0, 0), height=(-1, 0, 0), breadth=(0, 0, 1),
                 half_width=0.5, asymptote=0.1, copy=False):
        RPC.__init__(
            self, name=name, base=base, height=height,
            breadth=breadth, half_width=half_width, copy=copy
        )
        self.asymptote = asymptote

    def __repr__(self):
        return "{}({}, base={}, height={}, breadth={}, half_width={}, asymptote={})".format(
            self.__class__.__name__, self.name, repr(self.base),
            repr(self.height), repr(self.breadth), self.half_width, self.asymptote
        )

    def update_params(self, params):
        RPC.update_params(self, params)
        params.update({
            "asymptote": self.asymptote,
        })

    def copy(self):
        return RHC(self.name, base=self.base, height=self.height, breadth=self.breadth,
                   half_width=self.half_width, asymptote=self.asymptote, copy=True)

    def has_same_data(self, other):
        return RPC.has_same_data(self, other) and np.allclose(self.asymptote, other.asymptote)

    @staticmethod
    def from_wdb(name, data):
        return RHC(
            name=name,
            base=data.rhc_V,
            height=data.rhc_H,
            breadth=data.rhc_B,
            half_width=data.rhc_r,
            asymptote=data.rhc_c,
        )
