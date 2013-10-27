"""
This is the python version of globe.c using some ctypes bindings against
BRL-CAD.

globe.c header text:

    Creates a set of concentric "shells" that, when put together, comprise a
    unified solid spherical object.  Kinda like an onion, not a cake, an onion.

python attribution:

    :author: Kat Harrison <katherinej.harrison@gmail.com>
    :date: 2013-09-011
    :license: BSD

"""

import sys
import ctypes
import wdb


def main(argv):
    p1 = (ctypes.c_double * 3)()
    rgb = (ctypes.c_double * 3)()

    initialSize = 900.0
    finalSize = 1000.0
    stepSize = 10.0
    currentSize = 0.0
    counter = 0
    name = ""
    solidName = ""
    prevSolid = ""
    shaderparams = ""

    wm_hd = wdb.wmember()  # These are probably not necessary.
    bigList = wdb.wmember()

    db_fp = wdb.wdb_fopen(argv[1])

    wdb.mk_id(db_fp, "Globe Database")  # Create the database header record

    # Make a region that is the union of these two objectsion. To accomplish
    # this, we need to create a linked list of the items that make up the
    # combination. The wm_hd structure serves as the head of the list of items.
    somelistp = wdb.bu_list_new()
    biglistp = wdb.bu_list_new()

    # make the CORE of the globe with a given color
    p1[:] = [0, 0, 0]
    rgb[:] = [130, 253, 194]  # some green
    is_region = 1
    # make a sphere centered at 1.0, 2.0, 3.0 with radius .75
    wdb.mk_sph(db_fp, "land.s", p1, initialSize)
    wdb._libs.values()[0].mk_addmember("land.s", somelistp, wdb.NULL, ord("u"))
    wdb.mk_comb(db_fp,
                "land.c",
                somelistp,
                is_region,
                "",
                "",
                rgb,
                0, 0, 0,
                0, 0, 0,
                0)
    wdb._libs.values()[0].mk_addmember("land.s", somelistp, wdb.NULL, ord("u"))
    wdb.mk_comb(db_fp,
                "land.r",
                somelistp,
                is_region,
                "plastic",
                "di=.8 sp=.2",
                rgb,
                0, 0, 0,
                0, 0, 0,
                0)

    # make the AIR of the globe with a given color
    rgb[:] = [130, 194, 253]  # a light blue

    prevSolid = "land.s"
    counter = 0
    currentSize = initialSize + stepSize
    while currentSize < finalSize:
        somelistp = wdb.bu_list_new()

        solidName = "air.%d.s" % counter
        wdb.mk_sph(db_fp, solidName, p1, currentSize)
        wdb.mk_addmember(solidName, somelistp, wdb.NULL, ord("u"))
        wdb.mk_addmember(prevSolid, somelistp, wdb.NULL, ord("-"))

        # make the spatial combination
        name = "air.%d.c" % counter
        wdb.mk_comb(db_fp,
                    name,
                    somelistp,
                    0,
                    wdb.NULL,
                    wdb.NULL,
                    wdb.NULL,
                    0, 0, 0,
                    0, 0, 0,
                    0)
        wdb.mk_addmember(name, somelistp, wdb.NULL, ord("u"))

        # make the spatial region
        name = "air.%d.r" % counter
        shaderparams = "{tr %f}" % float(currentSize/finalSize)
        wdb.mk_comb(db_fp,
                    name,
                    somelistp,
                    is_region,
                    "plastic",
                    shaderparams,
                    rgb,
                    0, 0, 0,
                    0, 0, 0,
                    0)

        # add the region to a master region list
        wdb.mk_addmember(name, biglistp, wdb.NULL, ord("u"))

        # keep track of the last combination we made for the next iteration
        prevSolid = solidName

        counter += 1
        currentSize += stepSize

    # make one final air region that comprises all the air regions
    wdb.mk_comb(db_fp,
                "air.c",
                biglistp,
                0,
                wdb.NULL,
                wdb.NULL,
                wdb.NULL,
                0, 0, 0,
                0, 0, 0,
                0)

    # Create the master globe region
    #
    # In this case we are going to make it a region (hence the
    # is_region flag is set, and we provide shader parameter information.
    #
    # When making a combination that is NOT a region, the region flag
    # argument is 0, and the strings for optical shader, and shader
    # parameters should (in general) be null pointers.
    #
    # add the land to the main globe object that gets created at the end 
    somelistp = wdb.bu_list_new()
    wdb.mk_addmember("land.r", somelistp, wdb.NULL, ord("u"))
    wdb.mk_addmember("air.c", somelistp, wdb.NULL, ord("u"))

    wdb.mk_comb(db_fp,
                "globe.r",
                somelistp,
                is_region,
                wdb.NULL,
                wdb.NULL,
                wdb.NULL,
                0, 0, 0,
                0, 0, 0,
                0)

    wdb._libs.values()[0].wdb_close(db_fp)
    return 0


if __name__ == "__main__":
        main(sys.argv)
