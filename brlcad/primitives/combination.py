"""
Python wrapper for BRL-CAD combinations.
"""
import collections
import numpy as np
import brlcad._bindings.librt as librt
import brlcad.ctypes_adaptors as cta
from brlcad.exceptions import BRLCADException
from base import Primitive
from brlcad.vmath import Transform


def wrap_tree(*args):
    if len(args) == 1:
        args = args[0]
    if isinstance(args, (list, tuple)):
        if len(args) == 1 or (len(args) == 2 and isinstance(args[1], Transform)):
            return leaf(args)
        else:
            return union(*args)
    else:
        return leaf(args)


def leaf(*args):
    if len(args) == 1 and not isinstance(args, str):
        return LeafNode(args[0])
    else:
        return LeafNode(args)


def union(*args):
    return UnionNode(args)


def intersect(*args):
    return IntersectNode(args)


def negate(child):
    return NotNode(child)


def subtract(left, right):
    return SubtractNode(left, right)


def rsub(left, right):
    return SubtractNode(right, left)


def xor(*args):
    return XorNode(args)

#Primitive.__or__ = lambda self, other: union(self, other)
Primitive.__or__ = union
Primitive.__ror__ = union
Primitive.__and__ = intersect
Primitive.__rand__ = intersect
Primitive.__sub__ = subtract
Primitive.__rsub__ = rsub
Primitive.__xor__ = xor
Primitive.__rxor__ = xor
Primitive.__add__= intersect
Primitive.__radd__ = intersect


class TreeNode(object):
    def __new__(cls, node):
        if not isinstance(node, librt.union_tree):
            raise BRLCADException("It's not possible to instantiate this class directly, use one of it's subclasses")
        op_class = OP_MAP.get(node.tr_a.tu_op)
        if not op_class:
            raise BRLCADException("Invalid operation code: {0}".format(node.tr_a.tu_op))
        return op_class(node)

    __or__ = union
    __ror__ = union
    __and__ = intersect
    __rand__ = intersect
    __sub__ = subtract
    __rsub__ = rsub
    __xor__ = xor
    __rxor__ = xor
    __add__= intersect
    __radd__ = intersect


class LeafNode(TreeNode):
    def __new__(cls, arg):
        if isinstance(arg, TreeNode):
            # this is so that we can wrap all else but TreeNodes in a LeafNode:
            return arg
        result = object.__new__(cls)
        result.matrix = None
        if isinstance(arg, librt.union_tree):
            result.name = str(arg.tr_l.tl_name)
            if arg.tr_l.tl_mat:
                result.matrix = cta.transform_from_pointer(arg.tr_l.tl_mat)
        else:
            result.name = LeafNode.extract_name(arg)
            if not result.name:
                result.name = LeafNode.extract_name(arg[0])
                result.matrix = arg[1]
        return result

    def __repr__(self):
        if self.matrix:
            return "{0}({1})".format(self.name, self.matrix)
        else:
            return self.name

    @staticmethod
    def extract_name(arg):
        if isinstance(arg, str):
            return arg
        elif hasattr(arg, "name"):
            return arg.name
        else:
            return None

    def copy(self):
        return LeafNode((self.name, list(self.matrix) if self.matrix else None))

    def is_same(self, other):
        if not isinstance(other, LeafNode) or self.name != other.name:
            return False
        if self.matrix is not None:
            return other.matrix is not None and np.allclose(self.matrix, other.matrix)
        else:
            return other.matrix is None

    def build_tree(self):
        node = cta.brlcad_new(librt.struct_tree_db_leaf)
        node.magic = librt.RT_TREE_MAGIC
        node.tl_op = librt.OP_DB_LEAF
        node.tl_mat = None if self.matrix is None else cta.transform(self.matrix, use_brlcad_malloc=True)
        node.tl_name = librt.bu_strdupm(self.name, "tree_db_leaf.tl_name")
        return librt.cast(librt.pointer(node), librt.POINTER(librt.union_tree))


class NotNode(TreeNode):
    def __new__(cls, arg):
        if isinstance(arg, librt.union_tree):
            child = TreeNode(arg.tr_b.tb_left.contents)
        else:
            child = wrap_tree(arg)
        if isinstance(child, NotNode):
            return child.child
        result = object.__new__(cls)
        result.child = child
        return result

    def __repr__(self):
        return "not({0})".format(self.child)

    def copy(self):
        return NotNode(self.child.copy())

    def is_same(self, other):
        return isinstance(other, NotNode) and self.child.is_same(other.child)

    def build_tree(self):
        node = cta.brlcad_new(librt.struct_tree_node)
        node.magic = librt.RT_TREE_MAGIC
        node.tb_op = librt.OP_NOT
        node.tb_regionp = None
        node.tb_left = self.left.build_tree()
        return librt.cast(librt.pointer(node), librt.POINTER(librt.union_tree))


class SymmetricNode(TreeNode, collections.MutableSequence):

    def __new__(cls, arg):
        if isinstance(arg, librt.union_tree):
            left = TreeNode(arg.tr_b.tb_left.contents)
            right = TreeNode(arg.tr_b.tb_right.contents)
            arg = [left, right]
        else:
            if isinstance(arg, str):
                arg = [leaf(arg)]
            else:
                arg = [leaf(x) for x in arg]
        # if any of the children is of the same class, it will accumulate the new nodes:
        for i in xrange(0, len(arg)):
            if isinstance(arg[i], cls):
                for j in xrange(0, len(arg)):
                    if i != j:
                        arg[i].add_child(arg[j])
                return arg[i]
        result = object.__new__(cls)
        result.children = arg
        return result

    def __repr__(self):
        return "{0}{1}".format(self.symbol, self.children)

    def __len__(self):
        return len(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def __delitem__(self, index):
        del self.children[index]

    def index(self, child):
        return self.children.index(child)

    def insert(self, index, child):
        if index != len(self.children):
            raise NotImplemented
        self.add_child(child)

    def __setitem__(self, index, value):
        raise NotImplemented

    def add_child(self, child):
        if isinstance(child, type(self)):
            self.children.extend(child.children)
        else:
            self.children.append(wrap_tree(child))
        return self

    def copy(self):
        return self.__class__([x.copy() for x in self.children])

    def is_same(self, other):
        if not isinstance(other, self.__class__):
            return False
        if len(self.children) != len(other.children):
            return False
        return all([self.children[i].is_same(other.children[i]) for i in xrange(0, len(self.children))])

    def build_tree(self, subset=None):
        if subset and len(subset) == 1:
            return subset[0].build_tree()
        if not subset:
            subset = self.children
        node = cta.brlcad_new(librt.struct_tree_node)
        node.magic = librt.RT_TREE_MAGIC
        node.tb_op = self.op_code
        node.tb_regionp = None
        index = len(subset) / 2
        node.tb_left = self.build_tree(subset[:index])
        node.tb_right = self.build_tree(subset[index:])
        return librt.cast(librt.pointer(node), librt.POINTER(librt.union_tree))


class PairNode(TreeNode):
    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], librt.union_tree):
            node = args[0]
            left = TreeNode(node.tr_b.tb_left.contents)
            right = TreeNode(node.tr_b.tb_right.contents)
        elif len(args) == 2:
            left = wrap_tree(args[0])
            right = wrap_tree(args[1])
        else:
            raise BRLCADException("{0} needs 2 arguments !".format(cls))
        result = object.__new__(cls)
        result.left = left
        result.right = right
        result.symbol = cls.symbol
        return result

    def __repr__(self):
        return "({0} {1} {2})".format(self.left, self.symbol, self.right)

    def copy(self):
        return self.__class__(self.left.copy(), self.right.copy())

    def is_same(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.left.is_same(other.left) and self.right.is_same(other.right)

    def build_tree(self):
        node = cta.brlcad_new(librt.struct_tree_node)
        node.magic = librt.RT_TREE_MAGIC
        node.tb_op = self.op_code
        node.tb_regionp = None
        node.tb_left = self.left.build_tree()
        node.tb_right = self.right.build_tree()
        return librt.cast(librt.pointer(node), librt.POINTER(librt.union_tree))


class UnionNode(SymmetricNode):
    symbol = "u"
    op_code = librt.OP_UNION


class IntersectNode(SymmetricNode):
    symbol = "n"
    op_code = librt.OP_INTERSECT


class XorNode(SymmetricNode):
    symbol = "^"
    op_code = librt.OP_XOR


class SubtractNode(PairNode):
    symbol = "-"
    op_code = librt.OP_SUBTRACT


OP_MAP = {
    librt.OP_DB_LEAF: LeafNode,
    librt.OP_NOT: NotNode,
    librt.OP_UNION: UnionNode,
    librt.OP_INTERSECT: IntersectNode,
    librt.OP_SUBTRACT: SubtractNode,
    librt.OP_XOR: XorNode,
}


class Combination(Primitive):

    def __init__(self, name, tree=(), is_region=False, is_fastgen=0, inherit=False, shader=None,
                 material=None, rgb_color=None, temperature=0,
                 region_id=0, air_code=0, gift_material=0, line_of_sight=0):
        Primitive.__init__(self, name=name)
        self.tree = wrap_tree(tree)
        self.is_region = is_region
        self.is_fastgen = is_fastgen
        self.inherit = inherit
        self.shader = shader
        self.material = material
        self.rgb_color = rgb_color
        self.temperature = temperature
        self.region_id = region_id
        self.air_code = air_code
        self.gift_material = gift_material
        self.line_of_sight = line_of_sight

    def __repr__(self):
        return ''.join([
            "Combination(",
            "name=", self.name, ", ",
            "is_fastgen=", str(self.is_fastgen), ", ",
            "region_id=", str(self.region_id), ", ",
            "air_code=", str(self.air_code), ", ",
            "gift_material=", str(self.gift_material), ", ",
            "line_of_sight=", str(self.line_of_sight), ", ",
            "rgb_color=(", ','.join([str(x) for x in self.rgb_color]) if self.rgb_color else "None", "), ",
            "temperature=", str(self.temperature), ", ",
            "shader=", self.shader, ", ",
            "material=", self.material, ", ",
            "inherit=", str(self.inherit), ", ",
            str(self.tree), ")"
        ])

    def copy(self):
        return Combination(
            self.name, self.tree.copy(),
            is_region=self.is_region, is_fastgen=self.is_fastgen, inherit=self.inherit, shader=self.shader,
            material=self.material, rgb_color=(list(self.rgb_color) if self.rgb_color else None),
            temperature=self.temperature, region_id=self.region_id, air_code=self.air_code,
            gift_material=self.gift_material,line_of_sight=self.line_of_sight
        )

    def has_same_data(self, other):
        self_props = (
            self.name, self.is_fastgen, self.region_id, self.air_code, self.gift_material,
            self.line_of_sight, self.rgb_color, self.temperature, self.shader, self.material, self.inherit
        )
        other_props = (
            other.name, other.is_fastgen, other.region_id, other.air_code, other.gift_material,
            other.line_of_sight, self.rgb_color, other.temperature, other.shader, other.material, other.inherit
        )
        if self_props != other_props:
            return False
        return self.tree.is_same(other.tree)

    def update_params(self, params):
        params.update({
            "tree": self.tree,
            "is_region": self.is_region,
            "inherit": self.inherit,
            "shader": self.shader,
            "material": self.material,
            "rgb_color": self.rgb_color,
            "temperature": self.temperature,
            "region_id": self.region_id,
            "air_code": self.air_code,
            "gift_material": self.gift_material,
            "line_of_sight": self.line_of_sight,
            "is_fastgen": self.is_fastgen
        })


    @staticmethod
    def from_wdb(name, data):
        return Combination(
            name=name,
            tree=TreeNode(data.tree.contents),
            is_region=bool(data.region_flag),
            is_fastgen=ord(data.is_fastgen),
            region_id=data.region_id,
            air_code=data.aircode,
            gift_material=data.GIFTmater,
            line_of_sight=data.los,
            rgb_color=tuple(data.rgb) if data.rgb_valid else None,
            temperature=data.temperature,
            shader=str(data.shader.vls_str),
            material=str(data.material.vls_str),
            inherit=bool(data.inherit),
        )

