"""
Transformation matrices and operations using them.
"""

import numpy as np

class Transform(np.matrix):
    """
    A transformation, represented by a 4x4 matrix:

     x'   (R0  R1  R2  Dx)   x
     y' = (R4  R5  R6  Dy) * y
     z'   (R8  R9 R10  Dz)   z
     w'   (0   0   0  1/s)   w

    """

    def __new__(cls, data, copy=False):
        if isinstance(data, Transform) and data.dtype == np.float64:
            result = data.copy() if copy else data
        else:
            result = np.matrix.__new__(cls, data, dtype=np.float64, copy=copy)
        if result.shape != (4, 4):
            raise ValueError("A transform must be a 4x4 matrix, got: {0}".format(result.shape))
        return result

    @staticmethod
    def unit():
        return Transform("1, 0, 0, 0; 0, 1, 0, 0; 0, 0, 1, 0; 0, 0, 0, 1")

    @staticmethod
    def translation(dx, dy, dz):
        result = Transform.unit()
        result[0, 3] = dx
        result[1, 3] = dy
        result[2, 3] = dz
        return result
