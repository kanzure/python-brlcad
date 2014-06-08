"""
Python wrapper for the Bot primitive of BRL-CAD.
"""

from base import Primitive
from brlcad.vmath import Vector
import numpy as np
import brlcad.ctypes_adaptors as cta


class BOT(Primitive):
    def __init__(self, name, mode=3, orientation=1, flags=0, vertices=[[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0]],
                 faces = [[0, 1, 2], [1, 2, 3], [3, 1, 0]], thickness=[2, 3, 1], face_mode=[True, True,
                 False], copy=False):
        Primitive.__init__(self, name=name)
        self.mode=mode
        self.orientation=orientation
        self.flags=flags
        self.vertices = [Vector(vertex, copy) for vertex in vertices]
        if copy:
            self.faces = [face[:] for face in faces]
            self.face_mode = face_mode[:]
            self.thickness = thickness[:]
        else:
            self.faces = [face for face in faces]
            self.face_mode = face_mode
            self.thickness = thickness


    def __repr__(self):
        return "{}({}, mode={}, orientation={}, flags={}, vertices={}, faces={}, thickness={}, face_mode={})".format(
            self.__class__.__name__, self.name, self.mode, self.orientation, self.flags, self.vertices, self.faces,
            self.thickness, self.face_mode
        )

    def update_params(self, params):
        params.update({
            "mode": self.mode,
            "orientation": self.orientation,
            "flags": self.flags,
            "vertices": self.vertices,
            "faces": self.faces,
            "thickness": self.thickness,
            "face_mode": self.face_mode
        })

    def copy(self):
        return BOT(self.name, self.mode, self.orientation, self.flags, self.vertices, self.faces, self.thickness,
                   self.face_mode, copy=True)

    def has_same_data(self, other):
        return self.mode==other.mode and \
                self.orientation==other.orientation and \
                self.flags==other.flags and \
                np.allclose(self.vertices,other.vertices) and \
                np.allclose(self.faces,other.faces) and \
                np.allclose(self.thickness,other.thickness) and \
                self.face_mode==other.face_mode	\

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
        thickness = []
        face_mode = []
        if data.mode == 3:
            for i in range(data.num_faces):
                thickness.append(data.thickness[i])
                if cta.bit_test(data.face_mode, i):
                    face_mode.append(True)
                else:
                    face_mode.append(False)
        return BOT(
            name=name,
            mode=data.mode,
            orientation=data.orientation,
            flags=data.bot_flags,
            vertices=vertices,
            faces=faces,
            thickness=thickness,
            face_mode=face_mode
        )


