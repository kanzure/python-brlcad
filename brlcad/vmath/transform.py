"""
Transformation matrices and operations using them.
"""
from numbers import Number

import numpy as np
from vector import Vector


class Transform(np.matrix):
    """
    A transformation, represented by a 4x4 matrix:

     x'   (R0  R1  R2  Dx)   x
     y' = (R4  R5  R6  Dy) * y
     z'   (R8  R9 R10  Dz)   z
     w'   (0   0   0  1/s)   w

    """

    __array_priority__ = 15.0

    def __new__(cls, data, copy=False, force=False):
        if isinstance(data, Transform) and data.dtype == np.float64:
            result = data.copy() if copy else data
        else:
            result = np.matrix.__new__(cls, data, dtype=np.float64, copy=copy)
        if result.shape != (4, 4):
            if force:
                result = np.resize(result,(4,4))
            else :
                raise ValueError("A transform must be a 4x4 matrix, got: {0}".format(result.shape))
        return result

    @staticmethod
    def unit():
        return Transform("1, 0, 0, 0; 0, 1, 0, 0; 0, 0, 1, 0; 0, 0, 0, 1")

    @staticmethod
    def translation(dx, dy, dz):
        result = Transform.unit()
        result[0:3, 3] = (dx,), (dy,), (dz,)
        return result

    @staticmethod
    def scale(value):
        result = Transform.unit()
        result[3, 3] = value
        return result

    def __mul__(self, other):
        if isinstance(other, Number):
            return np.multiply(self, other)
        elif isinstance(other, np.matrix) and other.shape[0] == 4:
            return np.matrix.__mul__(self, other)
        elif isinstance(other, (np.ndarray, list, tuple)):
            if isinstance(other, (list, tuple)):
                other = Vector(other)
            should_extend = len(other) == 3
            if should_extend:
                other = list(other)
                other.append(1)
                other = Vector(other)
            result = Vector(np.matrix.__mul__(self, other.flat).flat)
            if should_extend:
                result[0:3] /= result[3]
                return result[0:3]
            else:
                return result
        return Vector(np.matrix.__mul__(self, other).flat)
