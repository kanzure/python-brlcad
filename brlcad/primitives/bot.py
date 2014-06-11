"""
Python wrapper for BOT (Bag of Triangles) primitives of BRL-CAD.
"""
import collections
import numbers

from base import Primitive
from brlcad.vmath import Vector
from brlcad.exceptions import BRLCADException
import brlcad._bindings.libbu as libbu
import brlcad.ctypes_adaptors as cta
import numpy as np


class Face:
    """
    Represents the face information in a bot.
    Each face has three integer values representing vertex indices of the triangle
    """
    def __init__(self, bot, vertices, index=None, copy=False):
        self.bot = bot
        self._points = list(vertices) if copy or not isinstance(vertices, list) else vertices
        if index==None:
            if len(vertices)==3:
                self.index=[]
                for i in xrange(0, len(self._points)):
                    self.index.append(bot.vertex_index(self._points[i]))
            else:
                raise BRLCADException("A face requires 3 vertices")
        else:
            self.index=index

    def has_same_data(self, other):
        return self.index == other.index

    def __repr__(self):
        return "{}(points={})".format(
            self.__class__.__name__, repr(self.index)
        )


class PlateFace(Face):
    """
    Represents a face of bot in plate mode
    if mode==true then it indicates thickness is appended to hit point in ray direction (if bit is set),
    otherwise thickness is centered about hit point
    """

    def __init__(self, bot, vertices, thickness=1, face_mode=True, copy=False):
        Face.__init__(self, bot, vertices, copy=copy)
        self.thickness = thickness
        self.face_mode = face_mode

    def __repr__(self):
        return "{}(points={}, thickness={}, mode={})".format(
            self.index, self.thickness, self.get_face_mode()
        )

    def get_face_mode(self):
        if self.face_mode:
            return "appended to hit point"
        else:
            return "centered about hit point"

    def has_same_data(self, other):
        return self.thickness == other.thickness and \
            self.index == other.index and \
            self.face_mode == other.face_mode


class BOT(Primitive):

    def __init__(self, name, mode=1, orientation=1, flags=0, vertices=None, faces=None, copy=False):
        Primitive.__init__(self, name=name)
        self.mode = mode
        self.orientation = orientation
        self.flags = flags
        if vertices is None:
            vertices = []
        elif not isinstance(vertices, list):
            vertices = list(vertices)
        for i in range(0, len(vertices)):
            vertices[i] = Vector(vertices[i], copy=copy)
        self.vertices = vertices
        if faces is None:
            faces = []
        elif not isinstance(faces, list):
            curves = list(faces)
        self.faces = faces
        for i in xrange(0, len(faces)):
                self.add_face(faces[i])

    def __repr__(self):
        return "{}(mode={}, orientation={}, flags={}, vertices={}, faces={}".format(
            self.__class__.__name__, self.getOrientation(), self.getMode(), self.flags, repr(self.vertices), repr(self.faces)
        )

    def getMode(self):
        if self.mode == 1:
            return "Surface"
        elif self.mode == 2:
            return "Solid"
        elif self.mode == 3:
            return "Plates"
        else:
            return "Plates Nocos"

    def getOrientation(self):
        if self.orientation == 1:
            return "Unoriented"
        elif self.orientation == 2:
            return "Counter Clockwise"
        else:
            return "Clockwise"

    def add_face(self, face):
        if self.mode == 1 or self.mode == 2:
            if isinstance(face,Face):
                 self.faces.append(face)
            else:
                raise BRLCADException("Invalid face type")
        elif self.mode == 3 or self.mode == 4:
            if isinstance(face,PlateFace):
                 self.faces.append(face)
            else:
                raise BRLCADException("Invalid face type")
        else:
            raise BRLCADException("Invalid mode")

    def data_validation(self):
        if len(self.faces):
            return True
        else:
            return False

    def vertex_index(self, value, copy=False):
        vertex_count = len(self.vertices)
        if isinstance(value, numbers.Integral):
            if value > vertex_count - 1:
                raise ValueError("Invalid vertex index: {}".format(value))
            return value
        value = Vector(value, copy=copy)
        if len(value) != 3:
            raise ValueError("A traingle needs 3D vertexes, but got: {}".format(value))
        for i in xrange(0, vertex_count):
            if self.vertices[i].is_same(value):
                return i
        self.vertices.append(value)
        return vertex_count

    def copy(self):
        return BOT(self.name, mode=self.mode, orientation=self.orientation, flags=self.flags,
                           vertices=self.vertices, faces=self.faces, copy=True)

    def has_same_data(self, other):
        return self.mode == other.mode and \
            all([self.faces[i].has_same_data(other.faces[i])for i in range(max(len(self.faces), len(other.faces)))])and\
            self.flags == other.flags and \
            self.orientation == other.orientation and \
            np.allclose(self.vertices,other.vertices)

    def update_params(self, params):
        thickness = []
        faces = []
        face_mode = []
        for i in range(len(self.faces)):
            faces.append(self.faces[i].index)
            if self.mode == 3:
                for i in range(len(self.faces)):
                    thickness.append(self.faces[i].thickness)
                    face_mode.append(self.faces[i].face_mode)
        params.update({
            "mode": self.mode,
            "orientation": self.orientation,
            "flags": self.flags,
            "vertices": self.vertices,
            "faces": faces,
            "thickness": thickness,
            "face_mode": face_mode
        })

    @staticmethod
    def from_wdb(name, data):
        vertices = []
        for i in range(data.num_vertices):
            vp1 = data.vertices[i*3+0]
            vp2 = data.vertices[i*3+1]
            vp3 = data.vertices[i*3+2]
            vertex = [vp1,vp2,vp3]
            vertices.append(vertex)
        faces = []
        for i in range(data.num_faces):
            fv1 = data.faces[i*3+0]
            fv2 = data.faces[i*3+1]
            fv3 = data.faces[i*3+2]
            face = [int(fv1), int(fv2), int(fv3)]
            faces.append(face)
        bot = BOT(name,mode=data.mode,orientation=data.orientation,flags=data.bot_flags,vertices=vertices)
        if data.mode == 3:
            for i in range(data.num_faces):
                bot.add_face(PlateFace(bot=bot, vertices=[vertices[x] for x in faces[i]], thickness=data.thickness[i],
                                       face_mode=cta.bit_test(data.face_mode, i)))
        else:
            for i in range(data.num_faces):
                bot.add_face(Face(bot=bot, vertices=[vertices[x] for x in faces[i]]))

        return bot


def BOT_SURFACE(name, orientation=1, flags=0, vertices=None, faces=None, copy=False):
    return BOT(name=name, mode=1, orientation=orientation, flags=flags, vertices=vertices, faces=faces, copy=copy)

def BOT_SOLID(name, orientation=1, flags=0, vertices=None, faces=None, copy=False):
    return BOT(name=name, mode=2, orientation=orientation, flags=flags, vertices=vertices, faces=faces, copy=copy)

def BOT_PLATES(name, orientation=1, flags=0, vertices=None, faces=None, copy=False):
    return BOT(name=name, mode=3, orientation=orientation, flags=flags, vertices=vertices, faces=faces, copy=copy)



