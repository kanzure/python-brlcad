"""
Python wrappers for the ARS primitives of BRL-CAD.
"""
from base import Primitive
import numpy as np
import brlcad.ctypes_adaptors as cta
from brlcad.exceptions import BRLCADException

def test_curves(curves):
    ### length of the curves should be more than 3.
    if len(curves) <=2:
        return False
    ### Check that first and last element have three entries i.e a single point
    if not (len(cta.flatten_numbers(curves[0])) == 3 and len(cta.flatten_numbers(curves[-1])) == 3):
        return False
    ### Check that the other curves contain atleast 3 points and each curve contain same number of points
    index_curve = len(cta.flatten_numbers(curves[1]))
    if index_curve % 3 != 0 and index_curve/3 >= 3:
        return False
    for i in range(2,len(curves)-1):
        if (len(cta.flatten_numbers(curves[i])) == index_curve):
            continue
        else:
            return False
    return True


class ARS(Primitive):

    def __init__(self, name, curves, copy=False):
        Primitive.__init__(self, name=name)
        if test_curves(curves):
            if copy:
                self.curves = [curve[:] for curve in curves]
            else:
                self.curves = curves
        else:
            print curves
            raise BRLCADException("Invalid Curve Data in Ars")

    def __repr__(self):
        result = "{}({}, name={}, curves={})"
        return result.format(
            self.__class__.__name__, repr(self.curves)
        )

    def update_params(self, params):
        ncurves = len(self.curves)
        pts_per_curve = len(cta.flatten_numbers(self.curves[1]))/3
        curves = [[None for x in range(pts_per_curve*3)] for y in range(ncurves)]
        ## for start
        for i in range(pts_per_curve):
            for j in range(3):
                curves[0][3*i+j] = self.curves[0][j]
        ##for other curves
        for i in range(1,ncurves-1):
            for j in range(3*pts_per_curve):
                curves[i][j] = self.curves[i][j]
        ## for end
        for i in range(pts_per_curve):
            for j in range(3):
                curves[ncurves-1][3*i+j] = self.curves[ncurves-1][j]
        params.update({
            "curves": curves
        })

    def copy(self):
        return ARS(self.name, self.curves, copy=True)

    def has_same_data(self, other):
        for i in range(len(self.curves)):
            if not np.allclose(self.curves[i], other.curves[i]):
                return False
        return True

    @staticmethod
    def from_wdb(name, data):
        ars_curves = cta.array2d_from_pointer(data.curves, data.ncurves, data.pts_per_curve*3)
        curves = list([list(curve) for curve in ars_curves])
        curves[0][3:] = []
        curves[-1][3:] = []
        return ARS(
            name=name,
            curves=curves
        )