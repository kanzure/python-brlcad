"""
Vector math based on numpy but targeting geometry operations.
"""
import numpy as np
import math


class Vector(np.ndarray):
    """
    Represents a vector as used in geometry applications.
    It is based on a numpy array but provides geometry specific operations.
    This is a generic Vector class which doesn't care about the number of
    space dimensions. Specific sub-classes will be used for specific number
    of space dimensions.

    Examples:
    """

    __array_priority__ = 20.0

    # noinspection PyNoneFunctionAssignment,PyArgumentList
    def __new__(cls, data, copy=True):
        """
        Constructor to handle most array-like data, and views and sub-lists as well.
        Examples:
        >>> Vector("1,2,3")
        Vector([ 1.,  2.,  3.])
        >>> x = np.array([4, 5, 6], dtype=np.float64)
        >>> Vector(x)
        Vector([ 4.,  5.,  6.])
        >>> y = x.view(Vector)
        >>> y
        Vector([ 4.,  5.,  6.])
        >>> x[1] = 7
        >>> y
        Vector([ 4.,  7.,  6.])
        >>> z = y[:2]
        >>> x[1] = 10
        >>> z
        Vector([  4.,  10.])

        A view will keep the original data type:
        >>> x = np.array([4, 5, 6], dtype=np.int32)
        >>> y = x.view(Vector)
        >>> y
        Vector([4, 5, 6])
        >>> y[1:]
        Vector([5, 6])

        Vectors will flatten arrays:
        >>> Vector([[1, 2, 3]])
        Vector([ 1.,  2.,  3.])
        >>> Vector([[1], [2], [3]])
        Vector([ 1.,  2.,  3.])

        A scalar is accepted as a vector;
        >>> Vector(1)
        Vector(1.0)
        """
        if isinstance(data, Vector):
            if data.dtype != np.float64:
                result = data.astype(np.float64)
            else:
                result = data
        elif isinstance(data, np.ndarray):
            result = data.view(cls)
            if result.dtype != np.float64:
                result = result.astype(np.float64)
        else:
            if isinstance(data, str):
                data = map(np.float64, data.split(','))
            new_data = np.array(data, dtype=np.float64, copy=copy)
            if new_data.ndim > 1:
                new_data = new_data.flatten()
            result = np.ndarray.__new__(cls, new_data.shape, np.float64, buffer=new_data, order=False)
            copy = False

        return result.copy() if copy else result

    # noinspection PyUnusedLocal
    def __array_finalize__(self, obj):
        """
        Makes sure the vectors always have only 1 axis. A scalar is an exception
        to the rule as it can be interpreted as a 1 component vector, and it is
        sometimes coming up as a result of numpy vector operations we want to support.
        Examples:
        >>> np.array([[1],[2],[3]]).view(Vector)
        Traceback (most recent call last):
        ...
        ValueError: Expected vector, got array with 2 dimensions

        Scalar is accepted as a vector;
        >>> np.array(1, dtype=np.int32).view(Vector)
        Vector(1)

        """
        if self.ndim > 1:
            raise ValueError("Expected vector, got array with {0} dimensions".format(self.ndim))

    def transpose(self):
        """
        This returns the transpose, which is _not_ a Vector !
        """
        return np.matrix(self).transpose()

    def norm(self):
        return math.sqrt(self.dot(self))

    def mag(self):
        return self.dot(self)

    def cross(self, other):
        """
        Cross product: self x other (not commutative !)
        >>> x = Vector("1, 0, 0")
        >>> y = Vector([0, 1, 0])
        >>> z = Vector((0, 0, 1))
        >>> x.cross(y).is_same(z)
        True
        >>> y.cross(x).is_same(-z)
        True
        """
        return Vector(np.cross(self, other))

    def is_same(self, other, rtol=1.e-5, atol=1.e-8):
        try:
            return np.allclose(self, other, rtol=rtol, atol=atol)
        except ValueError:
            return False

    def normalize(self):
        """
        Normalize this vector in place, and return it too.
        If the vector is all 0, will do nothing.
        >>> x = Vector("10, 0, 0")
        >>> y = x.normalize()
        >>> x
        Vector([ 1.,  0.,  0.])
        >>> x is y
        True
        >>> Vector("0,0,0").normalize()
        Vector([ 0.,  0.,  0.])
        """
        norm = self.norm()
        if not np.allclose(norm, 0) and not np.allclose(norm, 1):
            self.__idiv__(norm)
        return self

    def normal_copy(self):
        """
        Return a norm 1 copy of this vector. For all 0 vector will return all 0 too.
        >>> x = Vector("10, 0, 0")
        >>> y = x.normal_copy()
        >>> x
        Vector([ 10.,   0.,   0.])
        >>> y
        Vector([ 1.,  0.,  0.])
        """
        return self.copy().normalize()

    def assure_normal(self):
        """
        Return a norm 1 copy, or this vector if it is already of norm 0 or 1.
        >>> x = Vector("10, 0, 0")
        >>> y = x.assure_normal()
        >>> x
        Vector([ 10.,   0.,   0.])
        >>> y
        Vector([ 1.,  0.,  0.])
        >>> y is y.assure_normal()
        True
        """
        norm = self.norm()
        if np.allclose(norm, 0) or np.allclose(norm, 1):
            return self
        else:
            return self.copy().__idiv__(norm)

    def is_normal_to(self, other):
        """
        Returns True if this vector and other (vector-like) are perpendicular to each other.
        >>> Vector([1, 1, 0]).is_normal_to("0, 0, 1")
        True
        >>> x = Vector([1, 1, 1])
        >>> x.is_normal_to((0, 1, 0))
        False
        >>> x.is_normal_to([0, 1, -1])
        True
        """
        return np.allclose(self.dot(Vector(other)), 0)

    def construct_normal(self):
        """
        Returns a normal vector perpendicular to this vector.
        >>> x = Vector([1, 0, 0])
        >>> y = x.construct_normal()
        >>> x.is_normal_to(y)
        True
        >>> y.is_same([0, 0, -1])
        True
        >>> Vector([0, -1, 0]).construct_normal().is_same([0, 0, -1])
        True
        >>> Vector("1, 0").construct_normal().is_same([0, 1])
        True
        >>> Vector("3, -1, 2, -4").construct_normal().is_same([-0.8, 0, 0, -0.6])
        True
        """
        length = len(self)
        if length == 3:
            # for 3D vectors we try to be compatible with bn_vec_ortho from libbn
            indexes = (np.arange(length) + np.abs(self).argmin()) % length
            result = [0, 0, 0]
            result[indexes[1]] = -self[indexes[2]]
            result[indexes[2]] = self[indexes[1]]
        else:
            # this one will work for any vector length but it's not compatible with bn_vec_ortho
            i = np.abs(self).argmax()
            j = (i + 1) % length
            result = np.zeros(length)
            result[i] = -self[j]
            result[j] = self[i]
        return Vector(result).normalize()

    def compare_for_sort(self, other):
        """
        Compares 2 Vectors for sorting (used mostly when comparing 2 shapes).
        >>> Vector("1, 2, 3").compare_for_sort(Vector("1, 2, 3")) == 0
        True
        >>> Vector("2, 2, 3").compare_for_sort(Vector("1, 2, 3")) == 1
        True
        >>> Vector("1, 2, 3").compare_for_sort(Vector("1, 2, 4")) == -1
        True
        >>> Vector("1, 2").compare_for_sort(Vector("1, 2, 4")) == -1
        True
        >>> Vector("1, 2, 3").compare_for_sort(Vector("1, 2")) == 1
        True
        """
        length = len(self)
        result = length - len(other)
        if result:
            return result
        for i in xrange(0, length):
            result = self[i] - other[i]
            if result:
                return result
        return 0


def X():
    return Vector((1, 0, 0))


def Y():
    return Vector((0, 1, 0))


def Z():
    return Vector((0, 0, 1))


if __name__ == "__main__":
    import doctest
    np.set_printoptions(suppress=True, precision=5)
    doctest.testmod()
