"""
Python wrapper for BRL-CAD combinations.
"""
import brlcad._bindings.librt as librt

from brlcad.ctypes_adaptors import ct_transform_from_pointer, ct_transform, brlcad_new
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
    return LeafNode(args[0]) if len(args) == 1 and not isinstance(args, str) else LeafNode(args)


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
                result.matrix = ct_transform_from_pointer(arg.tr_l.tl_mat)
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

    def build_tree(self):
        node = brlcad_new(librt.struct_tree_db_leaf)
        node.magic = librt.RT_TREE_MAGIC
        node.tl_op = librt.OP_DB_LEAF
        node.tl_mat = None if self.matrix is None else ct_transform(self.matrix, use_brlcad_malloc=True)
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

    def build_tree(self):
        node = brlcad_new(librt.struct_tree_node)
        node.magic = librt.RT_TREE_MAGIC
        node.tb_op = librt.OP_NOT
        node.tb_regionp = None
        node.tb_left = self.left.build_tree()
        return librt.cast(librt.pointer(node), librt.POINTER(librt.union_tree))


class SymmetricNode(TreeNode):
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
        for i in range(0, len(arg)):
            if isinstance(arg[i], cls):
                for j in range(0, len(arg)):
                    if i != j:
                        arg[i].add_child(arg[j])
                return arg[i]
        result = object.__new__(cls)
        result.children = arg
        return result

    def __repr__(self):
        return "{0}{1}".format(self.symbol, self.children)

    def add_child(self, child):
        if isinstance(child, type(self)):
            self.children.extend(child.children)
        else:
            self.children.append(wrap_tree(child))
        return self

    def build_tree(self, subset=None):
        if subset and len(subset) == 1:
            return subset[0].build_tree()
        if not subset:
            subset = self.children
        node = brlcad_new(librt.struct_tree_node)
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

    def build_tree(self):
        node = brlcad_new(librt.struct_tree_node)
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

    def __init__(self, tree=None, is_region=False, type_id=None, db_internal=None, directory=None, data=None):
        Primitive.__init__(self, type_id=type_id, db_internal=db_internal, name=None, directory=directory, data=data)
        if tree:
            self.tree = wrap_tree(tree)
            self.is_region = is_region
        else:
            self.tree = TreeNode(data.tree.contents)
            self.is_region = data.region_flag

    def __repr__(self):
        if self.data.region_flag:
            return ''.join([
                "Region(",
                "name=", self.name, ", ",
                "fastgen=", str(ord(self.data.is_fastgen)), ", ",
                "region_id=", str(self.data.region_id), ", ",
                "aircode=", str(self.data.aircode), ", ",
                "GIFTmater=", str(self.data.GIFTmater), ", ",
                "los=", str(self.data.los), ", ",
                "rgb_valid=", str(ord(self.data.rgb_valid)), ", ",
                "rgb=(", ','.join([str(x) for x in self.data.rgb]), "), ",
                "temperature=", str(self.data.temperature), ", ",
                "shader=", str(self.data.shader.vls_str), ", ",
                "material=", str(self.data.material.vls_str), ", ",
                "inherit=", str(ord(self.data.inherit)), ", ",
                str(self.tree)
            ])
        else:
            return "Combination({0})".format(self.tree)

    def update_params(self, params):
        params.update({
            "db_internal": self.db_internal,
            "directory": self.directory,
            "data": self.data,
            "name": self.name
        })
        if self.is_region:
            pass
        else:
            pass
