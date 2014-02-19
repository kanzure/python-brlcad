"""
Python wrappers for the EPA and EHY primitives of BRL-CAD.
"""

from base import Primitive
from brlcad.vmath import Vector


class EPA(Primitive):

    def __init__(self, name, base=(0, 0, 0), height=(0, 0, 1), n_major=(0, 1, 0),
                 r_major=1, r_minor=0.5, copy=False):
        Primitive.__init__(self, name=name)
        self.base = Vector(base, copy=copy)
        self.height = Vector(height, copy=copy)
        self.n_major = Vector(n_major, copy=copy)
        self.r_major = r_major
        self.r_minor = r_minor

    def __repr__(self):
        return "{}({}, base={}, height={}, n_major={}, r_major={}, r_minor={})".format(
            self.__class__.__name__, self.name, repr(self.base), repr(self.height),
            repr(self.n_major), self.r_major, self.r_minor
        )

    def update_params(self, params):
        params.update({
            "base": self.base,
            "height": self.height,
            "n_major": self.n_major,
            "r_major": self.r_major,
            "r_minor": self.r_minor,
        })

    @staticmethod
    def from_wdb(name, data):
        return EPA(
            name=name,
            base=data.epa_V,
            height=data.epa_H,
            n_major=data.epa_Au,
            r_major=data.epa_r1,
            r_minor=data.epa_r2,
        )


class EHY(EPA):

    def __init__(self, name, base=(0, 0, 0), height=(0, 0, 1), n_major=(0, 1, 0),
                 r_major=1, r_minor=0.5, asymptote=0.1, copy=False):
        EPA.__init__(
            self, name=name, base=base, height=height, n_major=n_major,
            r_major=r_major, r_minor=r_minor, copy=copy
        )
        self.asymptote = asymptote

    def __repr__(self):
        return "{}({}, base={}, height={}, n_major={}, r_major={}, r_minor={}, asymptote={})".format(
            self.__class__.__name__, self.name, repr(self.base), repr(self.height),
            repr(self.n_major), self.r_major, self.r_minor, self.asymptote
        )

    def update_params(self, params):
        EPA.update_params(self, params)
        params.update({
            "asymptote": self.asymptote,
        })

    @staticmethod
    def from_wdb(name, data):
        return EHY(
            name=name,
            base=data.ehy_V,
            height=data.ehy_H,
            n_major=data.ehy_Au,
            r_major=data.ehy_r1,
            r_minor=data.ehy_r2,
            asymptote=data.ehy_c,
        )
