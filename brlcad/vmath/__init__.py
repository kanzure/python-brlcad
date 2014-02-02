"""
The python substitute for vmath.h - which mostly contains macros.
Not all macros are translated to python versions, only those which
are needed for the higher level operations implemented in python.
"""

from plane import *
from segment import *
from transform import *
from vector import *

__all__ = [Vector, Segment, Plane, Transform]
