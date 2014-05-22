from collections import Iterable
import ctypes
from numbers import Number
from brlcad.exceptions import BRLCADException
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


def iterate_numbers(container):
    """
    Iterator which flattens nested hierarchies of geometry to plain list of numbers.
    Some examples:
    >>> [x for x in iterate_numbers(2)]
    [2]
    >>> [x for x in iterate_numbers([3])]
    [3]
    >>> [x for x in iterate_numbers([(1,2,3),(4,5,6)])]
    [1, 2, 3, 4, 5, 6]
    """
    if isinstance(container, Number):
        yield container
    elif isinstance(container, np.ndarray):
        for x in container.flat:
            yield x
    elif isinstance(container, Iterable):
        for p in container:
            for x in iterate_numbers(p):
                yield x
    else:
        raise BRLCADException("Can't extract numbers from type: {0}".format(type(container)))


def flatten_numbers(container):
    """
    Flattens nested hierarchies of geometry to plain list of doubles.
    """
    return [x for x in iterate_numbers(container)]


def point(p, point_size=3):
    fp = [x for x in iterate_numbers(p)]
    if point_size != len(fp):
        raise BRLCADException("Expected {0} doubles, got: {1}".format(point_size, len(fp)))
    return (ctypes.c_double * point_size)(*fp)


def doubles(p, double_count=None, flatten=True):
    if double_count == 0:
        return None
    if not p:
        if double_count is None:
            return None
        actual_count = 0
    else:
        if flatten:
            p = [x for x in iterate_numbers(p)]
        actual_count = len(p)
    if double_count is not None and double_count != actual_count:
        raise BRLCADException("Expected {0} doubles, got: {1}".format(double_count, actual_count))
    if actual_count == 0:
        return None
    return (ctypes.c_double * actual_count)(*p)


def points(p, point_count=None, point_size=3):
    if point_count == 0:
        return None
    fp = [x for x in iterate_numbers(p)]
    double_count = len(fp)
    if point_count is not None:
        expected_count = point_count * point_size
        if expected_count != double_count:
            raise BRLCADException("Expected {} doubles, got: {}".format(expected_count, double_count))
    if double_count % point_size != 0:
        raise BRLCADException("Expected {}-tuples, got {} doubles !".format(point_size, double_count))
    return ctypes.cast((ctypes.c_double * double_count)(*fp), ctypes.POINTER(ctypes.c_double * point_size))


def points2D(p, point_count=None):
    return points(p, point_count=point_count, point_size=2)


def point2D(p):
    return point(p, point_size=2)


def direction(d):
    fp = [x for x in iterate_numbers(d)]
    double_count = len(fp)
    if double_count == 3:
        return (ctypes.c_double * 3)(*fp)
    elif double_count == 6:
        return (ctypes.c_double * 3)(fp[3] - fp[0], fp[4] - fp[1], fp[5] - fp[2])
    else:
        raise BRLCADException("Expected 3 oder 6 doubles, got: {0}".format(double_count))


def plane(p):
    fp = [x for x in iterate_numbers(p)]
    if len(fp) != 4:
        raise BRLCADException("Expected 4 doubles, got: {0}".format(len(fp)))
    return (ctypes.c_double * 4)(*fp)


def transform_from_pointer(t):
    return [t[x] for x in xrange(0, 16)]

def array2d_from_pointer(t) :
    result = [[t[i][j] for j in range(len(t[i])) ] for i in range(len(t))]
    return np.array(result)

def array2d(t):
    arrayPointers = []
    for i in range(len(t)):
        arrayPointer = (ctypes.c_double * len(t[i]))(*(t[i]))
        arrayPointers.append(arrayPointer)
    return ctypes_array(arrayPointer)

def transform(t, use_brlcad_malloc=False):
    """
    Serializes a Transform-like object 't' (can be anything which will provide 16 floats)
    to the ctypes form of a transformation matrix as used by BRL-CAD code.
    """
    fp = [x for x in iterate_numbers(t)]
    if len(fp) != 16:
        raise BRLCADException("Expected 16 doubles, got: {0}".format(len(fp)))
    result = (ctypes.c_double * 16)(*fp)
    if use_brlcad_malloc:
        result = brlcad_copy(result, "transform")
    return result


def planes(values):
    double_args = [x for x in iterate_numbers(values)]
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
        values = (128, 128, 128)
    return (ctypes.c_ubyte * 3)(*values)


def integers(values, flatten=True):
    if flatten:
        values = flatten_numbers(values)
    if not values:
        return None
    return (ctypes.c_int * len(values))(*values)


def str_to_vls(value):
    """
    Creates a VLS string with memory allocated by BRL-CAD code, must be also freed by BRL-CAD code.
    """
    result = libbn.bu_vls_vlsinit()
    if value is not None:
        libbn.bu_vls_strcat(result, libbn.String(value))
    return result.contents


def ctypes_array(pointer_list):
    """
    Turns the given list of ctypes pointers into an array of the pointed type.
    This won't work with 0 length lists as the ctypes type can't be inferred for those !
    All elements of the given list should be ctypes pointers of the same type.
    Only the first element is examined for the type extraction !
    """
    pointer_type = pointer_list[0]._type_
    return (pointer_type * len(pointer_list))(*[x.contents for x in pointer_list])


def ctypes_string_array(strings):
    """
    Turns a python string array into a C string (char *) array. A typical example would be to pass the
    command line arguments in the libged wrapper (see ged.py#execute_command).
    """
    return (ctypes.POINTER(ctypes.c_char) * len(strings))(
        *[ctypes.cast(x, ctypes.POINTER(ctypes.c_char)) for x in strings]
    )


if __name__ == "__main__":
    import doctest
    np.set_printoptions(suppress=True, precision=5)
    doctest.testmod()
