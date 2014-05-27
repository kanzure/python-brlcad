"""
Python wrappers for the ARS primitives of BRL-CAD.
"""
from base import Primitive
import numpy as np
import brlcad.ctypes_adaptors as cta
import os


class ARS(Primitive):

    def __init__(self, name, ncurves, pts_per_curve, curves, modified=True,copy=False):
        Primitive.__init__(self, name=name)
        if modified:
            mod_curves  = [[None for x in range(pts_per_curve*3)] for y in range(ncurves)]
            ## for start
            for i in range(pts_per_curve):
                for j in range(3):
                    mod_curves[0][3*i+j] = curves[0][j]
            ##for other curves
            for i in range(1,ncurves-1):
                for j in range(3*pts_per_curve):
                    mod_curves[i][j] = curves[i][j]
            ## for end
            for i in range(pts_per_curve):
                for j in range(3):
                    mod_curves[ncurves-1][3*i+j] = curves[ncurves-1][j]
        else:
            mod_curves = curves
        self.ncurves = ncurves
        self.pts_per_curve = pts_per_curve
        if copy:
            self.curves = [x[:] for x in mod_curves]
        else:
            self.curves = mod_curves

    def __repr__(self):
        result = "{}({}, name={}, ncurves={}, pts_per_curve={}, curves={})"
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
            name=name,
            ncurves=data.ncurves,
            pts_per_curve=data.pts_per_curve,
            curves=cta.array2d_from_pointer(data.curves,data.ncurves,data.pts_per_curve*3),
            modified=True
        )