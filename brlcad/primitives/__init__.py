"""
Python wrappers for the BRL-CAD primitives.
"""

from base import *
from arb8 import *
from arbn import *
from combination import *
from ellipsoid import *
from rpc import *
from tgc import *

__all__ = [
    "Primitive", "ARB8", "ARBN", "Ellipsoid", "Sphere", "RPC", "TGC", "Cone", "RCC", "TRC",
    "Combination", "negate", "intersect", "subtract", "union", "xor", "wrap_tree"
]
