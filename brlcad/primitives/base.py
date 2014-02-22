"""
Holds the base class for all primitives so we can have some common operations.
"""
from brlcad.exceptions import BRLCADException


class Primitive(object):

    def __init__(self, name, primitive_type=None, data=None):
        if not isinstance(name, str):
            raise ValueError("Primitive name must be a string, but got: {}".format(type(name)))
        self.name = name
        if primitive_type:
            self.primitive_type = primitive_type
            self.data = data

    def __repr__(self):
        return "{}(name={}, primitive_type={}, data={})".format(
            self.__class__.__name__, self.name, self.primitive_type, self.data
        )

    def update_params(self, params):
        """
        Prepare parameters for writing/updating this primitive in the DB file.
        Subclasses must override this method. The "name" parameter is already
        set, so it can be skipped.
        """
        raise NotImplementedError("Class {0} does not implement 'update_params' !".format(type(self)))

    def copy(self):
        raise BRLCADException("Primitive subclass {} does not implement copy !".format(self.__class__))

    def has_same_data(self, other):
        raise BRLCADException("Primitive subclass {} does not implement has_same_data !".format(self.__class__))

    def is_same(self, other):
        return isinstance(other, self.__class__) and self.name == other.name and self.has_same_data(other)

    @staticmethod
    def from_wdb(name, data):
        raise BRLCADException(
            "Bad setup in primitives/table.py for name: {}, data: {}, the from_wdb method must be overridden !".format(
                name, data
            )
        )
