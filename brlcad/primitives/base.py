"""
Holds the base class for all primitives so we can have some common operations.
"""


class Primitive(object):

    def __init__(self, type_id=None, db_internal=None, directory=None, data=None, name=None):
        self.type_id = type_id
        self.db_internal = db_internal
        self.directory = directory
        self.data = data
        self.name = name if name else str(directory.d_namep)

    def __repr__(self):
        return "{0}({1})".format(self.data, self.name)

    def update_params(self, params):
        """
        Prepare parameters for writing/updating this primitive in the DB file.
        Subclasses must override this method. The "name" parameter is already
        set, so it can be skipped.
        """
        raise NotImplementedError("Class {0} does not implement 'update_params' !".format(type(self)))
