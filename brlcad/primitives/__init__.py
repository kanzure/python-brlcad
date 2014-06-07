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
from torus import Torus, ETO
from epa import EPA, EHY
from hyperboloid import Hyperboloid
from particle import Particle
from pipe import Pipe, PipePoint
from sketch import Sketch, Extrude, Revolve
from vol import VOL
from ars import ARS
from half import Half
from superell import Superell
from metaball import Metaball
from ebm import EBM
from grip import Grip
from bot import BOT

__all__ = [
    "Primitive", "ARB8", "ARBN", "Ellipsoid", "Sphere", "Superell", "RPC", "RHC", "Particle", "VOL", "ARS",
    "Half", "TGC", "Cone", "RCC", "TRC", "Torus", "ETO", "EPA", "EHY", "Hyperboloid", "Pipe", "PipePoint",
    "Sketch", "Extrude", "Revolve", "Metaball", "EBM", "Grip", "BOT"
    "Combination", "negate", "intersect", "subtract", "union", "xor", "wrap_tree", "leaf"
]
