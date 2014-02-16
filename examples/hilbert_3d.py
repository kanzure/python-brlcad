"""
3D Hilbert space filling curve with pipes.
"""
from brlcad.vmath import Vector
from brlcad.wdb import WDB
import sys


XP = (1, 0, 0)
YP = (0, 1, 0)
ZP = (0, 0, 1)
XN = (-1, 0, 0)
YN = (0, -1, 0)
ZN = (0, 0, -1)

MAP = {
    XP: YN,
    YN: ZP,
    ZP: XN,
    XN: YP,
    YP: ZN,
    ZN: XP,
}

NEGATE = {
    XP: XN,
    YP: YN,
    ZP: ZN,
    XN: XP,
    YN: YP,
    ZN: ZP,
}


def generate_steps(level, direction=XP, order=(1, 1)):
    """
    Returns a generator for the direction of each step in a 3D Hilbert space filling curve.
    This is only one of the many possible variants, others can be obtained by changing
    the rules (in a consistent way).
    """
    if level == 0:
        return
    level -= 1
    o1 = order[0]
    o2 = order[1]
    side1 = MAP[direction]
    side2 = MAP[side1]
    side1_n = NEGATE[side1]
    side2_n = NEGATE[side2]
    if o1 < 0:
        side1, side1_n = side1_n, side1
    if o2 < 0:
        side2, side2_n = side2_n, side2
    op = o1 * o2
    for x in generate_steps(level, side1, (op, -o1)):
        yield x
    yield side1
    for x in generate_steps(level, side2, (-o2, -op)):
        yield x
    yield side2
    for x in generate_steps(level, side2, (-o2, -op)):
        yield x
    yield side1_n
    for x in generate_steps(level, direction, (-o1, -o2)):
        yield x
    yield direction
    for x in generate_steps(level, direction, (-o1, -o2)):
        yield x
    yield side1
    for x in generate_steps(level, side2_n, (-o2, op)):
        yield x
    yield side2_n
    for x in generate_steps(level, side2_n, (-o2, op)):
        yield x
    yield side1_n
    for x in generate_steps(level, side1_n, (-op, -o1)):
        yield x



def generate_points(iterations, direction=XP, order=(1, 1),
                    start_point=(0, 0, 0), x_vec=(1, 0, 0), y_vec=(0, 1, 0), z_vec=(0, 0, 1)):
    crt_point = Vector(start_point, copy=True)
    x_vec = Vector(x_vec, copy=False)
    y_vec = Vector(y_vec, copy=False)
    z_vec = Vector(z_vec, copy=False)
    yield crt_point
    for step in generate_steps(iterations, direction=direction, order=order):
        crt_point = crt_point + (step[0] * x_vec) + (step[1] * y_vec) + (step[2] * z_vec)
        yield crt_point


def hilbert_pipe(file_name, size=10, recursions=4, dc=0.2, direction=XP,
                 x_vec=(1, 0, 0), y_vec=(0, 1, 0), z_vec=(0, 0, 1)):
    l = float(size) / (2**recursions)
    d = dc * l
    r = d
    segments = [
        (x, d, 0, r) for x in
        generate_points(recursions, direction=direction,
                        x_vec=Vector(x_vec)*l, y_vec=Vector(y_vec)*l, z_vec=Vector(z_vec)*l)
    ]
    with WDB(file_name, "3D Hilbert space filling curve with pipes") as brl_db:
        pipe_name = "hilbert_3d.s"
        brl_db.pipe(pipe_name, segments=segments)
        region_name = "hilbert_3d.r"
        brl_db.region(name=region_name, tree=pipe_name, rgb_color=(64, 180, 96))


def hilbert_3D():
    if len(sys.argv) >= 2:
        file_name = sys.argv[1]
    else:
        file_name = "hilbert_3d.g"
    if len(sys.argv) >= 3:
        size = int(sys.argv[2])
    else:
        size = 10
    if len(sys.argv) >= 4:
        recursions = int(sys.argv[3])
    else:
        recursions = 2

    hilbert_pipe(file_name, size, recursions, direction=XP, x_vec=(2, 0.3, 0.3), y_vec=(0.3, 1, 0.3), z_vec=(0.3, 0.3, 1))


def hilbert_3D_test():
    l = 1
    d = 0.2 * l
    r = d
    with WDB("hilbert_3d_test.g", "Hilbert-pipe 3D") as brl_db:
        for o1 in (-1, 1):
            for o2 in (-1, 1):
                for crt_dir in NEGATE:
                    points_generator = generate_points(
                        2, direction=crt_dir, order=(o1, o2), x_vec=(l, 0, 0), y_vec=(0, l, 0), z_vec=(0, 0, l)
                    )
                    segments = [(x, d, 0, r) for x in points_generator]
                    shape_name = "hilbert_pipe_{}{}{}{}{}.s".format(o1, o2, *crt_dir)
                    region_name = "hilbert_pipe_{}{}{}{}{}.r".format(o1, o2, *crt_dir)
                    if min(crt_dir) < 0:
                        rgb_color = Vector("255, 0, 0")
                    else:
                        rgb_color = Vector("0, 255, 0")
                    if o1 < 0 or o2 < 0:
                        rgb_color *= 0.3
                        rgb_color += 60
                    brl_db.pipe(shape_name, segments=segments)
                    brl_db.region(name=region_name, tree=shape_name, rgb_color=tuple([int(c) for c in rgb_color]))


if __name__ == "__main__":
    # hilbert_3D_test()
    hilbert_3D()