"""
This is the python version of wdb_example.c using the python-brlcad module.

usage:

    python wdb_example.py output.g

    # want to render to file?
    rtedge -s 1024 -F output.pix output.g box_n_ball.r
    pix-png -s 1024 < output.pix > output.png

wdb_example.c header text:

    Create a BRL-CAD geometry database from C code.

    Note that this is for writing (creating/appending) a database.

    Note that since the values in the database are stored in millimeters, the
    arguments to the mk_* routines are constrained to also be in millimeters.

python attribution:

    :author: Bryan Bishop <kanzure@gmail.com>
    :date: 2013-09-09
    :license: BSD
"""

# sys has argv
import sys

from brlcad.primitives import union

import brlcad.wdb as wdb

def main(argv):
    with wdb.WDB(argv[1], "My Database") as brl_db:

        # All units in the database file are stored in millimeters. This constrains
        # the arguments to the mk_* routines to also be in millimeters.

        # make a sphere centered at 1.0, 2.0, 3.0 with radius 0.75
        brl_db.sphere("ball.s", center=(1, 2, 3), radius=0.75)

        # Make an rpp under the sphere (partly overlapping). Note that this really
        # makes an arb8, but gives us a shortcut for specifying the parameters.
        brl_db.rpp("box.s", pmin=(0, 0, 0), pmax=(2, 4, 2.5))

        # Make a region that is the union of these two objects. To accomplish
        # this, we don't need anymore to create any linked list of the items ;-).
        brl_db.combination(
            "box_n_ball.r",
            is_region=True,
            tree=union("ball.s", "box.s"),
            shader="plastic {di=.8 sp=.2}",
            rgb_color=(64, 180, 96)
        )

        # Makes a hole from one corner to the other of the box
        # Note that you can provide a single combination name or a list in the
        # obj_list parameter, it will be handled correctly, all the tedious list
        # building is done under the hood:
        brl_db.hole(
            hole_start=(0, 0, 0),
            hole_depth=(2, 4, 2.5),
            hole_radius=0.75,
            obj_list="box_n_ball.r"
        )


if __name__ == "__main__":
    main(sys.argv)
