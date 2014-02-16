"""
Python wrappers for the BRL-CAD primitives.
"""

from base import *
from arb8 import *
from arbn import *
from combination import *

__all__ = [Primitive, ARB8, ARBN, Combination, negate, intersect, subtract, union, xor, wrap_tree]
