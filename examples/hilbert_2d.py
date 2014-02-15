"""
Fractal pipes :-)
"""
from brlcad.vmath import Vector
from brlcad.wdb import WDB
import sys


UP = (1, 0)
VP = (0, 1)
UN = (-1, 0)
VN = (0, -1)

LEFT = {
    UP: VP,
    VP: UN,
    UN: VN,
    VN: UP,
}

NEGATE = {
    UP: UN,
    VP: VN,
    UN: UP,
    VN: VP,
}


def generate_steps(level, direction=UP, order=1):
    """
    Returns the direction of the next step.
    The recursive algorithm is:
    x(o) -> o*lx(-o), o*lx, x(o), x, x(o), -o*lx, -o*lx(-o)
    where:
    x -> current direction
    lx -> x turned to left (rotate) 90 degrees
    o -> determines on which side of the direction the next step will happen
    """
    if level == 0:
        return
    level -= 1
    if order > 0:
        side1 = LEFT[direction]
        side2 = NEGATE[side1]
    else:
        side2 = LEFT[direction]
        side1 = NEGATE[side2]
    for x in generate_steps(level, side1, -order):
        yield x
    yield side1
    for x in generate_steps(level, direction, order):
        yield x
    yield direction
    for x in generate_steps(level, direction, order):
        yield x
    yield side2
    for x in generate_steps(level, side2, -order):
        yield x


def generate_points(iterations, start_point=(0, 0, 0), u_vec=(0, 1, 0), v_vec=(0, 0, 1)):
    crt_point = Vector(start_point, copy=True)
    u_vec = Vector(u_vec, copy=False)
    v_vec = Vector(v_vec, copy=False)
    yield crt_point
    for x in generate_steps(iterations):
        crt_point = crt_point + (x[0] * u_vec) + (x[1] * v_vec)
        yield crt_point


def hilbert_pipe(file_name, size=10, recursions=4):
    l = float(size) / (2**recursions)
    d = 0.5 * l
    r = d
    segments = [(x, d, 0, r) for x in generate_points(recursions, u_vec=(0, l, 0), v_vec=(0, 0, l))]
    with WDB(file_name, "2D Hilbert space filling curve with pipes") as brl_db:
        pipe_name = "hilbert_2d.s"
        brl_db.pipe(pipe_name, segments=segments)
        region_name = "hilbert_2d.r"
        brl_db.region(name=region_name, tree=pipe_name, rgb_color=(64, 180, 96))


def hilbert_2d():
    if len(sys.argv) >= 2:
        file_name = sys.argv[1]
    else:
        file_name = "hilbert_2d.g"
    if len(sys.argv) >= 3:
        size = int(sys.argv[2])
    else:
        size = 10
    if len(sys.argv) >= 4:
        recursions = int(sys.argv[3])
    else:
        recursions = 4

    hilbert_pipe(file_name, size, recursions)


if __name__ == "__main__":
    hilbert_2d()
