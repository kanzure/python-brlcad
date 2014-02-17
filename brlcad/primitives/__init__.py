"""
Python wrappers for the BRL-CAD primitives.
"""

from base import Primitive
from arb8 import ARB8
from arbn import ARBN
from combination import Combination, negate, intersect, subtract, union, xor, wrap_tree, leaf
from ellipsoid import Ellipsoid, Sphere
from rpc import RPC
from tgc import TGC, Cone, RCC, TRC

__all__ = [
    "Primitive", "ARB8", "ARBN", "Ellipsoid", "Sphere", "RPC", "TGC", "Cone", "RCC", "TRC",
    "Combination", "negate", "intersect", "subtract", "union", "xor", "wrap_tree", "leaf"
]
