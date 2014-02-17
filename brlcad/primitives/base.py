"""
Holds the base class for all primitives so we can have some common operations.
"""
from brlcad.exceptions import BRLCADException


class Primitive(object):

    def __init__(self, name, primitive_type=None, data=None):
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

    @staticmethod
    def from_wdb(name, data):
        raise BRLCADException(
            "Bad setup in primitives/table.py for name: {}, data: {}, the from_wdb method must be overridden !".format(
                name, data
            )
        )
