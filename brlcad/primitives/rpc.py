"""
Python wrapper for the RPC primitive of BRL-CAD.
"""

from base import Primitive
from brlcad.vmath import Vector


class RPC(Primitive):

    def __init__(self, name, base=(0, 0, 0), height=(-1, 0, 0), breadth=(0, 0, 1), half_width=0.5, copy=False):
        Primitive.__init__(self, name=name, primitive_type="RPC")
        self.base = Vector(base, copy=copy)
        self.height = Vector(height, copy=copy)
        self.breadth = Vector(breadth, copy=copy)
        self.half_width = half_width

    def __repr__(self):
        return "RPC({}, base={}, height={}, breadth={}, half_width={})".format(
            self.name, repr(self.base), repr(self.height), repr(self.breadth), self.half_width
        )

    def update_params(self, params):
        params.update({
            "base": self.base,
            "height": self.height,
            "breadth": self.breadth,
            "half_width": self.half_width,
        })

    @staticmethod
    def from_wdb(name, data):
        return RPC(
            name=name,
            base=data.rpc_V,
            height=data.rpc_H,
            breadth=data.rpc_B,
            half_width=data.rpc_r,
        )
