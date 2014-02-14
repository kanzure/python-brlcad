"""
Fractal pipes :-)
"""
from brlcad.vmath import Vector, Transform
from brlcad.wdb import WDB
import sys


def hilbert_pipe(file_name, size=10, recursions=5):
    # we calculate the final feature sizes so we can skip scaling all vectors
    # in the recursive steps, and only need to do translations and rotation
    # TODO: check if one matrix can perhaps do all rotation+scale+translation in one step...
    l = float(size) / (2**(recursions + 1))
    d = l
    r = d
    segments = [
        Vector((0, -l, -l)),
        Vector((0, -l, l)),
        Vector((0, l, l)),
        Vector((0, l, -l)),
    ]
    # left bottom: rotation -PI/2 and translation
    delta_1 = Vector((0, -l, -l))
    rotation_1 = Transform("1,0,0,0; 0,0,1,0; 0,-1,0,0; 0,0,0,1")
    # left top: translation only
    delta_2 = Vector((0, -l, l))
    # right top: translation only
    delta_3 = Vector((0, l, l))
    # right bottom: rotation PI/2 and translation
    delta_4 = Vector((0, l, -l))
    rotation_4 = Transform("1,0,0,0; 0,0,-1,0; 0,1,0,0; 0,0,0,1")
    for i in range(0, recursions):
        delta_1 *= 2
        new_segments = [rotation_1 * x + delta_1 for x in segments]
        new_segments.reverse()
        delta_2 *= 2
        new_segments.extend([x + delta_2 for x in segments])
        delta_3 *= 2
        new_segments.extend([x + delta_3 for x in segments])
        delta_4 *= 2
        segments.reverse()
        new_segments.extend([rotation_4 * x + delta_4 for x in segments])
        segments = new_segments
    segments = [(x, d, 0, r) for x in segments]
    with WDB(file_name, "Hilbert-pipe") as brl_db:
        brl_db.pipe("hilbert_pipe.s", segments=segments)
        brl_db.region(name="hilbert_pipe.r", tree="hilbert_pipe.s", rgb_color=(64, 180, 96))

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        file_name = sys.argv[1]
    else:
        file_name = "hilbert_pipe.g"
    if len(sys.argv) >= 3:
        size = int(sys.argv[2])
    else:
        size = 10
    if len(sys.argv) >= 4:
        recursions = int(sys.argv[3])
    else:
        recursions = 5

    hilbert_pipe(file_name, size, recursions)
