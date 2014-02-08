"""
Python wrapper for BRL-CAD combinations.
"""
from brlcad import librt

from brlcad.ctypes_adaptors import ct_transform_from_pointer
from brlcad.exceptions import BRLCADException
from base import Primitive


class TreeNode(object):
    def __new__(cls, node):
        if not isinstance(node, librt.union_tree):
            raise BRLCADException("It's not possible to instantiate this class directly, use one of it's subclasses")
        op_class = OP_MAP.get(node.tr_a.tu_op)
        if not op_class:
            raise BRLCADException("Invalid operation code: {0}".format(node.tr_a.tu_op))
        return op_class(node)


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


class NotNode(TreeNode):
    def __new__(cls, arg):
        if isinstance(arg, librt.union_tree):
            child = TreeNode(arg.tr_b.tb_left.contents)
        else:
            child = LeafNode(arg)
        if isinstance(child, NotNode):
            return child.child
        result = object.__new__(cls)
        result.child = child
        return result

    def __repr__(self):
        return "not({0})".format(self.child)


class SymmetricNode(TreeNode):
    def __new__(cls, arg):
        if isinstance(arg, librt.union_tree):
            left = TreeNode(arg.tr_b.tb_left.contents)
            right = TreeNode(arg.tr_b.tb_right.contents)
            arg = [left, right]
        else:
            if isinstance(arg, str):
                arg = [LeafNode(arg)]
            else:
                arg = [LeafNode(x) for x in arg]
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
            self.children.append(LeafNode(child))
        return self


class PairNode(TreeNode):
    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], librt.union_tree):
            node = args[0]
            left = TreeNode(node.tr_b.tb_left.contents)
            right = TreeNode(node.tr_b.tb_right.contents)
        elif len(args) == 2:
            left = LeafNode(args[0])
            right = LeafNode(args[1])
        else:
            raise BRLCADException("{0} needs 2 arguments !".format(cls))
        result = object.__new__(cls)
        result.left = left
        result.right = right
        return result

    def __repr__(self):
        return "({0} {1} {2})".format(self.left, self.symbol, self.right)


class UnionNode(SymmetricNode):
    symbol = "u"


class IntersectNode(SymmetricNode):
    symbol = "n"


class XorNode(SymmetricNode):
    symbol = "^"


class SubtractNode(PairNode):
    symbol = "-"


OP_MAP = {
    librt.OP_DB_LEAF: LeafNode,
    librt.OP_NOT: NotNode,
    librt.OP_UNION: UnionNode,
    librt.OP_INTERSECT: IntersectNode,
    librt.OP_SUBTRACT: SubtractNode,
    librt.OP_XOR: XorNode,
}


class Combination(Primitive):

    def __init__(self, type_id, db_internal, directory, data):
        Primitive.__init__(self, type_id, db_internal, directory, data)
        self.tree = TreeNode(data.tree.contents)


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


def union(*args):
    return UnionNode(args)


def intersect(*args):
    return IntersectNode(args)


def negate(child):
    return NotNode(child)


def subtract(left, right):
    return SubtractNode(left, right)


def xor(*args):
    return XorNode(args)
