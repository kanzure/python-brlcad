
class Primitive(object):

    def __init__(self, type_id, db_internal, directory, data):
        self.type_id = type_id
        self.db_internal = db_internal
        self.directory = directory
        self.data = data
        self.name = str(directory.d_namep)

    def __repr__(self):
        return "{0}({1})".format(self.data, self.name)
