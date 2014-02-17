"""
Python wrapper for the TGC (Truncated General Cone) primitive of BRL-CAD.
"""

from base import Primitive
from brlcad.vmath import Vector


class TGC(Primitive):

    def __init__(self, name, base=(0, 0, 0), height=(0, 0, 1),
                 a=(0, 1, 0), b=(0.5, 0, 0), c=(0, 0.5, 0), d=(1, 0, 0),
                 copy=False):
        Primitive.__init__(self, name=name)
        self.base = Vector(base, copy=copy)
        self.height = Vector(height, copy=copy)
        self.a = Vector(a, copy=copy)
        self.b = Vector(b, copy=copy)
        self.c = Vector(c, copy=copy)
        self.d = Vector(d, copy=copy)

    def __repr__(self):
        return "TGC({}, base={}, height={}, a={}, b={}, c={}, d={})".format(
            self.name, repr(self.base), repr(self.height),
            repr(self.a), repr(self.b), repr(self.c), repr(self.d),
        )

    def update_params(self, params):
        params.update({
            "base": self.base,
            "height": self.height,
            "a": self.a,
            "b": self.b,
            "c": self.c,
            "d": self.d,
        })

    @staticmethod
    def from_wdb(name, data):
        return TGC(
            name=name,
            base=data.v,
            height=data.h,
            a=data.a,
            b=data.b,
            c=data.c,
            d=data.d,
        )


class TRC(TGC):

    def __new__(cls, name, base=(0, 0, 0), height=(0, 0, 1), r_base=1, r_top=0.5, copy=False):
        return TGC(
            name=name, base=base, height=height,
            a=(0, -r_base, 0), b=(r_base, 0, 0), c=(0, -r_top, 0), d=(r_top, 0, 0),
            copy=copy
        )


class Cone(TGC):

    def __new__(cls, name, base=(0, 0, 0), n=(0, 0, 1), h=1, r_base=1, r_top=0.5, copy=False):
        return TGC(
            name=name, base=base, height=Vector(n, copy=True)*h,
            a=(0, -r_base, 0), b=(r_base, 0, 0), c=(0, -r_top, 0), d=(r_top, 0, 0),
            copy=copy
        )


class RCC(TGC):

    def __new__(cls, name, base=(0, 0, 0), height=(0, 0, 1), radius=1, copy=False):
        base = Vector(base, copy=copy)
        height = Vector(height, copy=copy)
        a = height.construct_normal()
        b = a.cross(height)
        return TGC(name=name, base=base, height=height, a=a, b=b, c=a, d=b, copy=False)
