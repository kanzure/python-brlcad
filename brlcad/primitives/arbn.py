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

    def copy(self):
        return ARBN(self.name, self.planes, copy=True)

    def has_same_data(self, other):
        # This will return False if the planes are in different order,
        # but for the purposes this method is used for that's actually what we want
        return all(map(Plane.is_same, self.planes, other.planes))

    @staticmethod
    def from_wdb(name, data):
        return ARBN(
            name=name,
            planes=[data.eqn[i] for i in range(0, data.neqn)]
        )
