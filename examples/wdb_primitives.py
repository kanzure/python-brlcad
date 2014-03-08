from brlcad.vmath import Transform
from brlcad.wdb import WDB
from brlcad import primitives

if __name__ == "__main__":
    with WDB("test_wdb.g", "Test BRLCAD DB file") as brl_db:
        brl_db.sphere(
            "sph1.s",
            center=(1, 2, 3),
            radius=0.75
        )
        brl_db.rpp(
            "box1.s",
            pmin=(0, 0, 0),
            pmax=(2, 4, 2.5)
        )
        brl_db.wedge(
            "wedge1.s",
            vertex=(0, 0, 3.5),
            x_dir=(0, 1, 0),
            z_dir=(0, 0, 1),
            x_len=4, y_len=2, z_len=1,
            x_top_len=3
        )
        brl_db.arb4(
            "arb4.s",
            points=[(-1, -5, 3), (1, -5, 3), (1, -3, 4), (0, -4, 5)]
        )
        brl_db.arb5(
            "arb5.s",
            points=[(-1, -5, 0), (1, -5, 0), (1, -3, 0), (-1, -3, 0), (0, -4, 3)]
        )
        brl_db.arb6(
            "arb6.s",
            points=[(-1, -2.5, 0), (1, -2.5, 0), (1, -0.5, 0), (-1, -0.5, 0), (0, -2.5, 2.5), (0, -0.5, 2.5)]
        )
        brl_db.arb7(
            "arb7.s",
            points=[(-1, -2.5, 3), (1, -2.5, 3), (1, -0.5, 3), (-1, -1.5, 3), (-1, -2.5, 5), (1, -2.5, 5), (1, -1.5, 5)]
        )
        brl_db.arb8(
            "arb8.s",
            points=[
                (-1, -1, 5), (1, -1, 5), (1, 1, 5), (-1, 1, 5),
                (-0.5, -0.5, 6.5), (0.5, -0.5, 6.5), (0.5, 0.5, 6.5), (-0.5, 0.5, 6.5)
            ]
        )
        brl_db.ellipsoid(
            "ellipsoid.s",
            center=(0, -4, 6),
            a=(0.75, 0, 0),
            b=(0, 1, 0),
            c=(0, 0, 0.5)
        )
        brl_db.torus(
            "torus.s",
            center=(0, -2, 6),
            n=(0, 0, 1),
            r_revolution=1,
            r_cross=0.25
        )
        brl_db.rcc(
            "rcc.s",
            base=(1, 2, 5),
            height=(0, 0, 1),
            radius=1
        )
        brl_db.tgc(
            "tgc.s",
            base=(0, -5, 7),
            height=(0, 0, 1),
            a=(0.5, 0, 0),
            b=(0, 1, 0),
            c=(1, 0, 0),
            d=(0, 0.5, 0)
        )
        brl_db.cone(
            "cone.s",
            base=(0, -2, 7),
            n=(0, 0, 2),
            h=0.5,
            r_base=1.25,
            r_top=0.75
        )
        brl_db.trc(
            "trc.s",
            base=(0, -2, 7.5),
            height=(0, 0, 0.5),
            r_base=0.75,
            r_top=1.25
        )
        brl_db.rpc(
            "rpc.s",
            base=(0, -2, 8.5),
            height=(0, 0, 0.5),
            breadth=(0.25, 0.25, 0),
            half_width=0.75
        )
        brl_db.rhc(
            "rhc.s",
            base=(0, -2, 9),
            height=(0, 0, 0.5),
            breadth=(0.25, 0.25, 0),
            half_width=0.75,
            asymptote=0.1
        )
        brl_db.epa(
            "epa.s",
            base=(1, 2, 7),
            height=(0, 0, -1),
            n_major=(1, 0, 0),
            r_major=1,
            r_minor=0.5
        )
        brl_db.ehy(
            "ehy.s",
            base=(1, 2, 7),
            height=(0, 0, 1),
            n_major=(1, 0, 0),
            r_major=1, r_minor=0.5,
            asymptote=0.1
        )
        brl_db.hyperboloid(
            "hyperboloid.s",
            base=(0, 0, 6.75),
            height=(0, 0, 0.75),
            a_vec=(1, 0, 0),
            b_mag=0.5,
            base_neck_ratio=0.3
        )
        brl_db.eto(
            "eto.s",
            center=(1, 2, 8.5),
            n=(0, 0, 1),
            s_major=(0.5, 0, 0.5),
            r_revolution=1,
            r_minor=0.25
        )
        brl_db.arbn(
            "arbn.s",
            planes=[
                [(0, 0, -1), -8],
                [(0, 0, 1), 9],
                [(-1, 0, 0), 0.5],
                [(1, 0, 0), 0.5],
                [(0, -1, 0), 0.5],
                [(0, 1, 0), 0.5],
            ]
        )
        brl_db.particle(
            "particle.s",
            base=(0, -5, 8.5),
            height=(0, 0, 0.75),
            r_base=0.25,
            r_end=0.5
        )
        brl_db.pipe(
            "pipe.s",
            points=[
                [(0.55, 4, 5.45), 0.1, 0, 0.45],
                [(0.55, 3.55, 5.4875), 0.1, 0, 0.45],
                [(1.45, 3.55, 5.5625), 0.1, 0, 0.45],
                [(1.45, 4.45, 5.6375), 0.1, 0, 0.45],
                [(0.55, 4.45, 5.7125), 0.1, 0, 0.45],
                [(0.55, 3.55, 5.7875), 0.1, 0, 0.45],
                [(1.45, 3.55, 5.8625), 0.1, 0, 0.45],
                [(1.45, 4.45, 5.9375), 0.1, 0, 0.45],
                [(0.55, 4.45, 6.0125), 0.1, 0, 0.45],
                [(0.55, 4, 6.05), 0.1, 0, 0.45],
            ]
        )
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
            shader="plastic {di .8 sp .2}",
            rgb_color=(64, 180, 96)
        )

    with WDB("test_wdb.g") as brl_db:
        for x in brl_db.ls():
            print brl_db.lookup(x)
