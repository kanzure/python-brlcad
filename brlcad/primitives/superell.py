"""
Python wrappers for the SUPERELL primitives of BRL-CAD.
"""
from base import Primitive
from brlcad.vmath import Vector, Transform, Plane
import numpy as np
import brlcad.ctypes_adaptors as cta

class SUPERELL(Primitive):

    def __init__(self,name, v=(0, 0, 0), a=(1, 0, 0), b=(0, 1, 0), c=(0, 0, 1), n=0, e=0, copy=False):
        Primitive.__init__(self, name=name)
        self.v = Vector(v, copy)
        self.a = Vector(a, copy)
        self.b = Vector(b, copy)
        self.c = Vector(c, copy)
        self.n = n
        self.e = e

    def __repr__(self):
        result = "{}({}, v={}, a={}, b={}, c={}, n={}, e={} )"
        return result.format(
            self.__class__.__name__, self.name, repr(self.v), repr(self.a),
            repr(self.b), repr(self.c), self.n, self.e
        )

    def update_params(self, params):
        params.update({
            "v": self.v,
            "a": self.a,
            "b": self.b,
            "c": self.c,
            "n": self.n,
            "e": self.e
        })

    def copy(self):
        return SUPERELL(self.name, self.v, self.a, self.b, self.c, self.n, self.e, copy=True)

    def has_same_data(self, other):
        return self.e == other.e and \
               self.n == other.n and \
               self.v.is_same(other.v) and \
               self.a.is_same(other.a) and \
               self.b.is_same(other.b) and \
               self.c.is_same(other.c)

    @staticmethod
    def from_wdb(name, data):
        return SUPERELL(
            name=name,
            v=data.v,
            a=data.a,
            b=data.b,
            c=data.c,
            n=data.n,
            e=data.e,
        )