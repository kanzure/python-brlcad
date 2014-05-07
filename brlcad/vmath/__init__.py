"""
The python substitute for vmath.h - which mostly contains macros.
Not all macros are translated to python versions, only those which
are needed for the higher level operations implemented in python.
"""

from plane import Plane
from segment import Segment
from transform import Transform
from vector import Vector
from triangle import Triangle
from arc import Arc

__all__ = ["Vector", "Segment", "Plane", "Transform", "Arc", "Triangle"]
