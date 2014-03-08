"""
This is the python version of globe.c using the python-brlcad libwdb wrapper.

globe.c header text:

    Creates a set of concentric "shells" that, when put together, comprise a
    unified solid spherical object.  Kinda like an onion, not a cake, an onion.

python attribution:

    :author: Csaba Nagy <IRC:javampire>
    :date: 2014-03-08
    :license: BSD

"""

import argparse
from brlcad.wdb import WDB
from brlcad.primitives import subtract, union


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="Creates a set of concentric \"shells\" that, when put together, comprise a"
                    " unified solid spherical object. Kinda like an onion, not a cake, an onion."
    )
    parser.add_argument("db_file")
    parser.add_argument("step_size", type=float, nargs="?", default=50.0)
    parser.add_argument("final_size", type=float, nargs="?", default=1000.0)
    parser.add_argument("initial_size", type=float, nargs="?", default=800.0)
    return parser.parse_args(args)


def main():
    args = parse_args()
    origin = (0, 0, 0)
    # color for the core (land):
    green = (130, 253, 194)
    # color for the air:
    light_blue = (130, 194, 253)
    with WDB(args.db_file, "Globe Database") as globe_db:
        globe_db.sphere("land.s", center=origin, radius=args.initial_size)
        # the core is a region (is_region=True) and it has the shader set:
        globe_db.combination(
            "land.r",
            tree="land.s",
            is_region=True,
            rgb_color=green,
            shader="plastic {di .8 sp .2}",
        )
        # each layer is formed by subtracting the former sphere from the current sphere
        # the core land is the first "former sphere":
        prev_solid = "land.s"
        counter = 0
        current_size = args.initial_size + args.step_size
        # this will collect the air layers:
        air_list = []
        while current_size < args.final_size:
            crt_solid = "air.{}.s".format(counter)
            crt_comb = "air.{}.c".format(counter)
            crt_air = "air.{}.r".format(counter)
            globe_db.sphere(crt_solid, center=origin, radius=current_size)
            globe_db.combination(
                crt_comb,
                tree=subtract(crt_solid, prev_solid)
            )
            # Each layer is a region with it's own transparency setting:
            globe_db.combination(
                crt_air,
                tree=crt_comb,
                is_region=True,
                shader="plastic {{tr {}}}".format(current_size/args.final_size),
                rgb_color=light_blue,
                air_code=counter,
                region_id=counter
            )
            air_list.append(crt_air)
            prev_solid = crt_solid
            current_size += args.step_size
            counter += 1
        # the air layers are grouped here in a combination,
        # not in a region as they are already regions on their own:
        globe_db.combination(
            "air.g",
            tree=union(air_list),
        )
        # the final group of core land + air layers (no region, the leafs are already regions):
        globe_db.combination(
            "globe.g",
            tree=union("land.r", "air.g"),
        )
        # load the resulting geometry file in mged, ray-trace with a white background, enjoy :-)


if __name__ == "__main__":
        main()
