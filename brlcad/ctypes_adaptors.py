from collections import Iterable
import ctypes
from numbers import Number
from exceptions import BRLCADException
import numpy as np
import brlcad._bindings.libbn as libbn


def brlcad_new(obj_type, debug_msg=None):
    """
    Returns a new obj of class <obj_type> using a buffer allocated via bu_malloc.
    Needed for creating objects which will be freed by BRL-CAD code.
    """
    if not debug_msg:
        debug_msg = obj_type.__class__.__name__
    count = ctypes.sizeof(obj_type)
    obj_buf = libbn.bu_malloc(count, debug_msg)
    return obj_type.from_address(obj_buf)


def brlcad_copy(obj, debug_msg):
    """
    Returns a copy of the obj using a buffer allocated via bu_malloc.
    This is needed when BRLCAD frees the memory pointed to by the passed in pointer - yes that happens !
    """
    count = ctypes.sizeof(obj)
    obj_copy = libbn.bu_malloc(count, debug_msg)
    ctypes.memmove(obj_copy, ctypes.addressof(obj), count)
    return type(obj).from_address(obj_copy)


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


def flatten_floats(container):
    """
    Flattens nested hierarchies of geometry to plain list of doubles.
    """
    return [x for x in iterate_doubles(container)]


def points(p, point_count=1):
    fp = [x for x in iterate_doubles(p)]
    expected_count = point_count * 3
    double_count = len(fp)
    if expected_count != double_count:
        raise BRLCADException("Expected {0} doubles, got: {1}".format(expected_count, double_count))
    return (ctypes.c_double * double_count)(*fp)


def direction(d):
    fp = [x for x in iterate_doubles(d)]
    double_count = len(fp)
    if double_count == 3:
        return (ctypes.c_double * 3)(*fp)
    elif double_count == 6:
        return (ctypes.c_double * 3)(fp[3] - fp[0], fp[4] - fp[1], fp[5] - fp[2])
    else:
        raise BRLCADException("Expected 3 oder 6 doubles, got: {0}".format(double_count))


def plane(p):
    fp = [x for x in iterate_doubles(p)]
    if len(fp) != 4:
        raise BRLCADException("Expected 4 doubles, got: {0}".format(len(fp)))
    return (ctypes.c_double * 4)(*fp)


def transform_from_pointer(t):
    return [t[x] for x in range(0, 16)]


def transform(t, use_brlcad_malloc=False):
    """
    Serializes a Transform-like object 't' (can be anything which will provide 16 floats)
    to the ctypes form of a transformation matrix as used by BRL-CAD code.
    """
    fp = [x for x in iterate_doubles(t)]
    if len(fp) != 16:
        raise BRLCADException("Expected 16 doubles, got: {0}".format(len(fp)))
    result = (ctypes.c_double * 16)(*fp)
    if use_brlcad_malloc:
        result = brlcad_copy(result, "transform")
    return result


def planes(values):
    double_args = [x for x in iterate_doubles(values)]
    count = len(double_args)
    if count % 4 != 0:
        raise ValueError("Invalid parameter count ({}) for planes !".format(count))
    return (ctypes.c_double * count)(*double_args)


def pointer(value):
    return ctypes.byref(value)


def bool(value):
    return 1 if value else 0


def bool_to_char(value):
    return '\1' if value else '\0'


def int_to_char(value):
    return str(chr(value))


def rgb(values):
    if values is None:
        return None
    return chr(values[0]) + chr(values[1]) + chr(values[2])


def str_to_vls(value):
    """
    Creates a VLS string with memory allocated by BRL-CAD code, must be also freed by BRL-CAD code.
    """
    result = libbn.bu_vls_vlsinit()
    if value is not None:
        libbn.bu_vls_strcat(result, libbn.String(value))
    return result.contents
