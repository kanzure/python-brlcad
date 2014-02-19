"""
Python wrappers for the BRL-CAD primitives.
"""

from base import Primitive
from arb8 import ARB8
from arbn import ARBN
from combination import Combination, negate, intersect, subtract, union, xor, wrap_tree, leaf
from ellipsoid import Ellipsoid, Sphere
from rpc import RPC, RHC
from tgc import TGC, Cone, RCC, TRC
from torus import Torus

__all__ = [
    "Primitive", "ARB8", "ARBN", "Ellipsoid", "Sphere", "RPC", "RHC",
    "TGC", "Cone", "RCC", "TRC", "Torus",
    "Combination", "negate", "intersect", "subtract", "union", "xor", "wrap_tree", "leaf"
]
