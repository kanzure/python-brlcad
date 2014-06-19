"""
Python wrappers for the Submodel primitives of BRL-CAD.
"""
from base import Primitive
from brlcad.vmath import Transform
import numpy as np
import brlcad.ctypes_adaptors as cta
import os


class Submodel(Primitive):

    def __init__(self, name, file_name, treetop, method=1, copy=False):
        Primitive.__init__(self, name=name)
        if not os.path.isfile(file_name):
            raise ValueError("File {} does not exist !".format(file_name))
        self.file_name = file_name
        self.treetop = treetop
        self.method = method

    def __repr__(self):
        result = "{}({}, file_name={}, treetop={}, method={})"
        return result.format(
            self.__class__.__name__, self.name, self.file_name, self.treetop, self.method)

    def update_params(self, params):
        params.update({
            "file_name": self.file_name,
            "treetop": self.treetop,
            "method": self.method
        })

    def copy(self):
        return Submodel(self.name, self.file_name, self.treetop, self.method, copy=True)

    def has_same_data(self, other):
        return self.file_name == other.file_name and \
               self.treetop == other.treetop and \
               self.method == other.method

    @staticmethod
    def from_wdb(name, data):
        return Submodel(
            name=name,
            file_name=data.file.vls_str.data,
            treetop=data.treetop.vls_str.data,
            method=1
        )