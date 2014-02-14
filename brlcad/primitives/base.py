"""
Holds the base class for all primitives so we can have some common operations.
"""


class Primitive(object):

    def __init__(self, name, primitive_type):
        self.name = name
        self.primitive_type = primitive_type

    def __repr__(self):
        return "{0}({1})".format(self.primitive_type, self.name)

    def update_params(self, params):
        """
        Prepare parameters for writing/updating this primitive in the DB file.
        Subclasses must override this method. The "name" parameter is already
        set, so it can be skipped.
        """
        raise NotImplementedError("Class {0} does not implement 'update_params' !".format(type(self)))

    @staticmethod
    def from_wdb(name, data):
        return Primitive(name=name, primitive_type=data)
