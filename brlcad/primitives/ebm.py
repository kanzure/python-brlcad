"""
Python wrappers for the EBM primitives of BRL-CAD.
"""
from base import Primitive
from brlcad.vmath import Vector, Transform
import numpy as np
import brlcad.ctypes_adaptors as cta
import os


class EBM(Primitive):

    def __init__(self, name, file_name, x_dim=350, y_dim=350, tallness=20, mat=Transform.unit(), copy=False):
        Primitive.__init__(self, name=name)
        if not os.path.isfile(file_name):
            raise ValueError("File {} does not exist !".format(file_name))
        self.file_name = file_name
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.tallness = tallness
        self.mat = Transform(mat, copy=copy, force=True)

    def __repr__(self):
        result = "{}({}, file_name={}, x_dim={}, y_dim={}, tallness={}, mat={})"
        return result.format(
            self.__class__.__name__, self.name, self.file_name, self.x_dim, self.y_dim, self.tallness,
            repr(self.mat)
        )

    def update_params(self, params):
        params.update({
            "file_name": self.file_name,
            "x_dim": self.x_dim,
            "y_dim": self.y_dim,
            "tallness": self.tallness,
            "mat": self.mat
        })

    def copy(self):
        return EBM(self.name, self.file_name, self.x_dim, self.y_dim, self.tallness, self.mat, copy=True)

    def has_same_data(self, other):
        if not (self.file_name == other.file_name, self.x_dim == other.x_dim and self.y_dim == other.y_dim and
                self.tallness == other.tallness):
            return False
        return np.allclose(self.mat, other.mat)


    @staticmethod
    def from_wdb(name, data):
        return EBM(
            name=name,
            file_name=data.file,
            x_dim=data.xdim,
            y_dim=data.ydim,
            tallness=data.tallness,
            mat=cta.transform_from_pointer(data.mat)
        )