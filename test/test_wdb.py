from brlcad.vmath import Transform
from brlcad.wdb import WDB
from brlcad import primitives

if __name__ == "__main__":
    with WDB("test_wdb.g", "Test BRLCAD DB file") as brl_db:
        brl_db.sphere("sph1.s", (1, 2, 3), 0.75)
        brl_db.rpp("box1.s", (0, 0, 0), (2, 4, 2.5))
        brl_db.wedge("wedge1.s", (0, 0, 3.5), (0, 1, 0), (0, 0, 1), 4, 2, 1, 3)
        brl_db.arb4("arb4.s", (-1, -5, 3, 1, -5, 3, 1, -3, 4,
                                0, -4, 5))
        brl_db.arb5("arb5.s", (-1, -5, 0, 1, -5, 0, 1, -3, 0, -1, -3, 0,
                                0, -4, 3))
        brl_db.arb6("arb6.s", (-1, -2.5, 0,   1, -2.5, 0, 1, -0.5, 0, -1, -0.5, 0,
                                0, -2.5, 2.5, 0, -0.5, 2.5))
        brl_db.arb7("arb7.s", (-1, -2.5, 3, 1, -2.5, 3, 1, -0.5, 3, -1, -1.5, 3,
                               -1, -2.5, 5, 1, -2.5, 5, 1, -1.5, 5))
        brl_db.arb8("arb8.s", (-1,  -1,   5,   1,   -1,   5,   1,   1,   5,   -1,   1,   5,
                               -0.5,-0.5, 6.5, 0.5, -0.5, 6.5, 0.5, 0.5, 6.5, -0.5, 0.5, 6.5))
        brl_db.ellipsoid("ellipsoid.s", (0, -4, 6), (0.75, 0, 0), (0, 1, 0), (0, 0, 0.5))
        brl_db.torus("torus.s", (0, -2, 6), (0, 0, 1), 1, 0.25)
        brl_db.rcc("rcc.s", (1, 2, 5), (0, 0, 1), 1)
        brl_db.tgc("tgc.s", (0, -5, 7), (0, 0, 1), (0.5, 0, 0), (0, 1, 0), (1, 0, 0), (0, 0.5, 0))
        brl_db.cone("cone.s", (0, -2, 7), (0, 0, 2), 0.5, 1.25, 0.75)
        brl_db.trc("trc.s", (0, -2, 7.5), (0, 0, 0.5), 0.75, 1.25)
        brl_db.trc_top("trc_top.s", (0, -2, 8), (0, -2, 8.5), 1.25, 0.75)
        brl_db.rpc("rpc.s", (0, -2, 8.5), (0, 0, 0.5), (0.25, 0.25, 0), 0.75)
        brl_db.rhc("rhc.s", (0, -2, 9), (0, 0, 0.5), (0.25, 0.25, 0), 0.75, 0.1)
        brl_db.epa("epa.s", (1, 2, 7), (0, 0, -1), (1, 0, 0), 1, 0.5)
        brl_db.ehy("ehy.s", (1, 2, 7), (0, 0, 1), (1, 0, 0), 1, 0.5, 0.1)
        brl_db.hyperboloid("hyperboloid.s", (0, 0, 6.75), (0, 0, 0.75), (1, 0, 0), 0.5, 0.3)
        brl_db.eto("eto.s", (1, 2, 8.5), (0, 0, 1), (0.5, 0, 0.5), 1, 0.25)
        brl_db.arbn("arbn.s", [
            (0, 0, -1, -8), (0, 0, 1, 9), (-1, 0, 0, 0.5), (1, 0, 0, 0.5), (0, -1, 0, 0.5), (0, 1, 0, 0.5)
        ])
        brl_db.particle("particle.s", (0, -5, 8.5), (0, 0, 0.75), 0.25, 0.5)
        brl_db.pipe("pipe.s", [
            ((0.55, 4, 5.45), 0.1, 0, 0.45),
            ((0.55, 3.55, 5.4875), 0.1, 0, 0.45),
            ((1.45, 3.55, 5.5625), 0.1, 0, 0.45),
            ((1.45, 4.45, 5.6375), 0.1, 0, 0.45),
            ((0.55, 4.45, 5.7125), 0.1, 0, 0.45),
            ((0.55, 3.55, 5.7875), 0.1, 0, 0.45),
            ((1.45, 3.55, 5.8625), 0.1, 0, 0.45),
            ((1.45, 4.45, 5.9375), 0.1, 0, 0.45),
            ((0.55, 4.45, 6.0125), 0.1, 0, 0.45),
            ((0.55, 4, 6.05), 0.1, 0, 0.45),
        ])
        brl_db.region(
            name="all.r",
            tree=(
                "sph1.s",
                "box1.s",
                "wedge1.s",
                "arb4.s",
                "arb5.s",
                "arb6.s",
                "arb7.s",
                "arb8.s",
                "ellipsoid.s",
                "torus.s",
                "rcc.s",
                "tgc.s",
                "cone.s",
                "trc.s",
                "trc_top.s",
                "rpc.s",
                "rhc.s",
                "epa.s",
                "ehy.s",
                "hyperboloid.s",
                "eto.s",
                primitives.leaf("arbn.s", Transform.translation(1, 0, 0)),
                "particle.s",
                "pipe.s",
            ),
            shader="plastic {di=.8 sp=.2}", rgb_color=(64, 180, 96),
            region_id=1
        )

    with WDB("test_wdb.g") as brl_db:
        print brl_db.lookup_internal("arb8.s")
        print brl_db.lookup_internal("all.r")
        print brl_db.lookup_internal("box1.s")
        print brl_db.lookup_internal("arb4.s")
        print brl_db.lookup_internal("sph1.s")
