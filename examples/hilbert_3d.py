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

# The fields returned are what needs to be done in each step:
# (connecting direction, recursion direction, mirroring params)
VARIANTS = [
    lambda args: (
        (args.side1, args.side1, (args.om, -args.o1)),
        (args.side2, args.side2, (-args.o2, -args.om)),
        (args.side1_n, args.direction, (args.o1, args.o2)),
        (args.direction, args.side2, (args.o2, args.om)),
        (args.side1, args.side2_n, (args.o2, -args.om)),
        (args.side2_n, args.direction, (args.o1, args.o2)),
        (args.side1_n, args.side2_n, (-args.o2, args.om)),
        (None, args.side1_n, (-args.om, -args.o1)),
    ),
    lambda args: (
        (args.side1, args.side1, (args.om, -args.o1)),
        (args.side2, args.side2, (-args.o2, -args.om)),
        (args.side1_n, args.side2, (-args.o2, -args.om)),
        (args.direction, args.direction, (-args.o1, -args.o2)),
        (args.side1, args.direction, (-args.o1, -args.o2)),
        (args.side2_n, args.side2_n, (-args.o2, args.om)),
        (args.side1_n, args.side2_n, (-args.o2, args.om)),
        (None, args.side1_n, (-args.om, -args.o1)),
    ),
]


class ShapeArgs(object):
    def __init__(self, direction, order):
        self.direction = direction
        self.o1, self.o2 = order
        self.side1 = MAP[direction]
        self.side2 = MAP[self.side1]
        self.side1_n = NEGATE[self.side1]
        self.side2_n = NEGATE[self.side2]
        if self.o1 < 0:
            self.side1, self.side1_n = self.side1_n, self.side1
        if self.o2 < 0:
            self.side2, self.side2_n = self.side2_n, self.side2
        self.om = self.o1 * self.o2


def generate_steps(level, direction=XP, order=(1, 1), variant=0):
    """
    Returns a generator for the direction of each step in a 3D Hilbert space filling curve.
    There are many possible variants, others can be obtained by changing  the rules
    (in a consistent way) in the VARIANTS map.
    """
    if level == 0:
        return
    level -= 1
    shape_args = ShapeArgs(direction, order)
    steps = VARIANTS[variant](shape_args)
    for i in range(0, len(steps)):
        crt_step = steps[i]
        for x in generate_steps(level, direction=crt_step[1], order=crt_step[2], variant=variant):
            yield x
        if crt_step[0]:
            yield crt_step[0]


def generate_points(iterations, direction=XP, order=(1, 1), variant=0,
                    start_point=(0, 0, 0), x_vec=(1, 0, 0), y_vec=(0, 1, 0), z_vec=(0, 0, 1)):
    crt_point = Vector(start_point, copy=True)
    x_vec = Vector(x_vec, copy=False)
    y_vec = Vector(y_vec, copy=False)
    z_vec = Vector(z_vec, copy=False)
    yield crt_point
    for step in generate_steps(iterations, direction=direction, order=order, variant=variant):
        crt_point = crt_point + (step[0] * x_vec) + (step[1] * y_vec) + (step[2] * z_vec)
        yield crt_point


def hilbert_pipe(file_name, size=10, recursions=4, dc=0.2, direction=ZP, variant=0,
                 x_vec=(1, 0, 0), y_vec=(0, 1, 0), z_vec=(0, 0, 1)):
    l = float(size) / (2**recursions)
    d = dc * l
    r = d
    points = [
        (x, d, 0, r) for x in
        generate_points(recursions, direction=direction, variant=variant,
                        x_vec=Vector(x_vec)*l, y_vec=Vector(y_vec)*l, z_vec=Vector(z_vec)*l)
    ]
    with WDB(file_name, "3D Hilbert space filling curve with pipes") as brl_db:
        pipe_name = "hilbert_3d.s"
        brl_db.pipe(pipe_name, points=points)
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

    # hilbert_pipe(file_name, size, recursions, direction=XP, x_vec=(2, 0.3, 0.3), y_vec=(0.3, 1, 0.3), z_vec=(0.3, 0.3, 1))
    hilbert_pipe(file_name, size, recursions)


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
                    brl_db.pipe(shape_name, points=segments)
                    brl_db.region(name=region_name, tree=shape_name, rgb_color=tuple([int(c) for c in rgb_color]))


if __name__ == "__main__":
    # hilbert_3D_test()
    hilbert_3D()