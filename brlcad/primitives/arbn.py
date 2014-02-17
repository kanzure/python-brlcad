"""
Python wrapper for the ARBN primitive of BRL-CAD.
"""

from base import Primitive
from brlcad.vmath import Plane


class ARBN(Primitive):

    def __init__(self, name, planes, copy=False):
        Primitive.__init__(self, name=name)
        self.planes = [Plane.from_values(x, copy=copy) for x in planes]

    def __repr__(self):
        return "ARBN({0}, {1})".format(self.name, repr(self.planes))

    def update_params(self, params):
        params.update({
            "planes": self.planes,
        })

    @staticmethod
    def from_wdb(name, data):
        return ARBN(
            name=name,
            planes=[data.eqn[i] for i in range(0, data.neqn)]
        )
