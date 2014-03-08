"""
Python wrappers for the VOL primitives of BRL-CAD.
"""

from base import Primitive
from brlcad.vmath import Vector


class VOL(Primitive):

    def __init__(self, name, x_dim=0, y_dim=0, z_dim=0, low_thresh=0, high_thresh=1, cell_size=(0,0,0), mat=None,
                 copy=False):
        Primitive.__init__(self, name=name)
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.z_dim = z_dim
        self.low_thresh = low_thresh
        self.high_thresh = high_thresh
        self.cell_size = Vector(cell_size,copy)
        self.mat = mat


    def __repr__(self):
        return "{}({}, x_dim={}, y_dim={}, z_dim={}, low_thresh={}, high_thresh={} cell_size={}, mat={})".format(
            self.__class__.__name__, self.name, self.x_dim, self.y_dim, self.z_dim, self.low_thresh,
            self.high_thresh, repr(self.cell_size), repr(self.mat)
        )

    def update_params(self, params):
        params.update({
            "x_dim" : self.x_dim,
            "y_dim" : self.y_dim,
            "z_dim" : self.z_dim,
            "low_thresh" : self.low_thresh,
            "high_thresh" :self.high_thresh,
            "cell_size" :self.cell_size,
            "mat" : self.mat
        })

    def copy(self):
        return VOL(self, self.name, self.x_dim, self.y_dim, self.z_dim, self.low_thresh, self.high_thresh,
                   self.cell_size, self.mat, copy=True)

    def has_same_data(self, other):
        if not (self.x_dim == other.x_dim and self.y_dim == other.y_dim and self.z_dim == other.z_dim and
                self.low_thresh == other.low_thresh and self.high_thresh == other.high_thresh) :
            return False
        self_vectors = (self.cell_size, self.mat)
        other_vectors = (other.cell_size, other.mat)
        return all(map(Vector.is_same, self_vectors, other_vectors))

    @staticmethod
    def from_wdb(name, data):
        return VOL(
            name=name,
            x_dim=data.x_dim,
            y_dim=data.y_dim,
            z_dim=data.z_dim,
            low_thresh=data.low_thresh,
            high_thresh=data.high_thresh,
            cell_size=data.cell_size,
            mat=data.mat,
        )