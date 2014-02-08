from collections import Iterable
import ctypes
from ctypes import c_double
from numbers import Number
from exceptions import BRLCADException
import numpy as np


def iterate_doubles(container):
    """
    Iterator which flattens nested hierarchies of geometry to plain list of doubles.
    """
    for p in container:
        if isinstance(p, Number):
            yield p
        elif isinstance(p, np.ndarray):
            for x in p.flat:
                yield x
        elif isinstance(p, Iterable):
            for x in p:
                yield x
        else:
            raise BRLCADException("Can't extract doubles from type: {0}".format(type(p)))


def ct_points(p, point_count=1):
    fp = [x for x in iterate_doubles(p)]
    expected_count = point_count * 3
    double_count = len(fp)
    if expected_count != double_count:
        raise BRLCADException("Expected {0} doubles, got: {1}".format(expected_count, double_count))
    return (ctypes.c_double * double_count)(*fp)


def ct_direction(d):
    fp = [x for x in iterate_doubles(d)]
    double_count = len(fp)
    if double_count == 3:
        return (ctypes.c_double * 3)(*fp)
    elif double_count == 6:
        return (ctypes.c_double * 3)(fp[3] - fp[0], fp[4] - fp[1], fp[5] - fp[2])
    else:
        raise BRLCADException("Expected 3 oder 6 doubles, got: {0}".format(double_count))


def ct_plane(p):
    fp = [x for x in iterate_doubles(p)]
    if len(fp) != 4:
        raise BRLCADException("Expected 4 doubles, got: {0}".format(len(fp)))
    return (ctypes.c_double * 4)(*fp)


def ct_transform_from_pointer(t):
    return [t[x] for x in range(0, 16)]


def ct_transform(t):
    fp = [x for x in iterate_doubles(t)]
    if len(fp) != 16:
        raise BRLCADException("Expected 16 doubles, got: {0}".format(len(fp)))
    return (ctypes.c_double * 16)(*fp)


def ct_planes(planes):
    double_args = [x for x in iterate_doubles(planes)]
    return (ctypes.c_double * len(double_args))(*double_args)


def ct_pointer(value):
    return ctypes.byref(value)


def ct_bool(value):
    return 1 if value else 0


def ct_rgb(values):
    if values:
        return chr(values[0]) + chr(values[1]) + chr(values[2])
    else:
        return None
