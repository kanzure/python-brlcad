"""
Python wrappers for the VOL primitives of BRL-CAD.
"""
from base import Primitive
import numpy as np
import brlcad.ctypes_adaptors as cta
import os


class ARS(Primitive):

    def __init__(self, name, ncurves, pts_per_curve, curves, copy=False):
        Primitive.__init__(self, name=name)
        self.ncurves = ncurves
        self.pts_per_curve = pts_per_curve
        if copy:
            self.curves = cta.array2d(curves, ncurves, pts_per_curve*3)
        else:
            self.curves = curves

    def __repr__(self):
        result = "{}({}, file_name={}, x_dim={}, y_dim={}, z_dim={}, " \
                 "low_thresh={}, high_thresh={} cell_size={}, mat={})"
        return result.format(
            self.__class__.__name__, self.name, self.ncurves, self.pts_per_curve, repr(self.curves)
        )

    def update_params(self, params):
        params.update({
            "ncurves": self.ncurves,
            "pts_per_curve":self.pts_per_curve,
            "curves":self.curves
        })

    def copy(self):
        return ARS(self.name,self.ncurves,self.pts_per_curve,self.curves, copy=True)

    def has_same_data(self, other):
        if not (self.pts_per_curve == other.pts_per_curve and self.ncurves == other.ncurves):
            return False
        return np.allclose(self.curves, other.curves)


    @staticmethod
    def from_wdb(name, data):
        return ARS(
            name=data.name,
            ncurves=data.ncurves,
            pts_per_curve=data.pts_per_curve,
            curves=cta.array2d_from_pointer(data.curves, data.ncurves, data.pts_per_curve*3)
        )