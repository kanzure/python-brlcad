"""
Python wrapper for libwdb adapting python types to the needed ctypes structures.
"""
import fnmatch
import brlcad._bindings.libwdb as libwdb
from brlcad.vmath import Transform
import os
from brlcad.util import check_missing_params
import brlcad.ctypes_adaptors as cta
from brlcad.exceptions import BRLCADException
import brlcad.primitives.table as p_table
import brlcad.primitives as primitives

# This is unfortunately needed because the original signature
# has an array of doubles and ctpyes refuses to take None as value for that
libwdb.mk_addmember.argtypes = [
    libwdb.String, libwdb.POINTER(libwdb.struct_bu_list), libwdb.POINTER(libwdb.c_double), libwdb.c_int
]


# This map holds the primitive type -> mk_... method mapping for saving each type of primitives.
# It is populated by the mk_wrap_primitive decoration.
SAVE_MAP = {}


def mk_wrap_primitive(primitive_class):
    def wrapper_func(mk_func):
        if primitive_class == primitives.Primitive:
            pass
        elif SAVE_MAP.has_key(primitive_class) and SAVE_MAP[primitive_class] != mk_func:
            raise BRLCADException(
                "Bad setup, multiple save functions ({}, {}) assigned to primitive: {}".format(
                    mk_func, SAVE_MAP[primitive_class], primitive_class
                )
            )
        else:
            def wrapped_func(db_self, *args, **kwargs):
                if len(args) == 1 and isinstance(args[0], primitives.Primitive):
                    shape = args[0]
                    if not isinstance(shape, primitive_class):
                        raise(
                            "{0} expects primitive of type {1} but got {2}".format(
                                mk_func.func_name, primitive_class, type(shape)
                            )
                        )
                    shape.update_params(kwargs)
                    mk_func(db_self, shape.name, **kwargs)
                else:
                    mk_func(db_self, *args, **kwargs)
            SAVE_MAP[primitive_class] = wrapped_func
        return mk_func
    return wrapper_func


class WDB:
    """
    Object to open or create a BRLCad data base file and read/write/modify it.
    """

    def __init__(self, db_file, title=None):
        try:
            self.db_fp = None
            if os.path.isfile(db_file):
                self.db_ip = libwdb.db_open(db_file, "r+w")
                if self.db_ip == libwdb.DBI_NULL:
                    raise BRLCADException("Can't open existing DB file: <{0}>".format(db_file))
                if libwdb.db_dirbuild(self.db_ip) < 0:
                    raise BRLCADException("Failed loading directory of DB file: <{}>".format(db_file))
                self.db_fp = libwdb.wdb_dbopen(self.db_ip, libwdb.RT_WDB_TYPE_DB_DISK)
                if self.db_fp == libwdb.RT_WDB_NULL:
                    raise BRLCADException("Failed read existing DB file: <{}>".format(db_file))
            if not self.db_fp:
                self.db_fp = libwdb.wdb_fopen(db_file)
                if self.db_fp == libwdb.RT_WDB_NULL:
                    raise BRLCADException("Failed creating new DB file: <{}>".format(db_file))
                self.db_ip = self.db_fp.contents.dbip
                if title:
                    libwdb.mk_id(self.db_fp, title)
        except Exception as e:
            raise BRLCADException("Can't open DB file <{0}>: {1}".format(db_file, e))

    def __iter__(self):
        for i in xrange(0, libwdb.RT_DBNHASH):
            dp = self.db_ip.contents.dbi_Head[i]
            while dp:
                crt_dir = dp.contents
                yield crt_dir
                dp = crt_dir.d_forw

    def ls(self, pattern=None):
        name_generator = (str(x.d_namep) for x in self if not(x.d_flags & libwdb.RT_DIR_HIDDEN))
        return [x for x in name_generator if pattern is None or fnmatch.fnmatch(name=x, pat=pattern)]

    def _lookup_internal(self, name):
        db_internal = libwdb.rt_db_internal()
        dpp = libwdb.pointer(libwdb.POINTER(libwdb.directory)())
        idb_type = libwdb.rt_db_lookup_internal(
            self.db_ip, name,
            dpp,
            libwdb.byref(db_internal),
            libwdb.LOOKUP_QUIET,
            libwdb.byref(libwdb.rt_uniresource)
        )
        # TODO: the "directory" structure is leaked here perhaps ?
        return idb_type, db_internal, dpp

    def lookup(self, name):
        idb_type, db_internal, dpp = self._lookup_internal(name)
        if not idb_type:
            return None
        return p_table.create_primitive(idb_type, db_internal, dpp.contents.contents)

    def delete(self, name):
        idb_type, db_internal, dpp = self._lookup_internal(name)
        if not idb_type:
            return False
        result1 = not libwdb.db_delete(self.db_ip, dpp.contents)
        result2 = not libwdb.db_dirdelete(self.db_ip, dpp.contents)
        return result1 and result2

    def close(self):
        libwdb.wdb_close(self.db_fp)

    @mk_wrap_primitive(primitives.Sphere)
    def sphere(self, name, center=(0, 0, 0), radius=1):
        libwdb.mk_sph(self.db_fp, name, cta.point(center), radius)

    @mk_wrap_primitive(primitives.Primitive)
    def rpp(self, name, pmin=(-1, -1, -1), pmax=(1, 1, 1)):
        libwdb.mk_rpp(self.db_fp, name, cta.point(pmin), cta.point(pmax))

    @mk_wrap_primitive(primitives.Primitive)
    def wedge(self, name, vertex=(0, 0, 0), x_dir=(1, 0, 0), z_dir=(0, 0, 1),
              x_len=1, y_len=1, z_len=1, x_top_len=0.5):
        libwdb.mk_wedge(self.db_fp, name,
                        cta.point(vertex), cta.direction(x_dir), cta.direction(z_dir),
                        x_len, y_len, z_len, x_top_len)

    @mk_wrap_primitive(primitives.Primitive)
    def arb4(self, name, points=(0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1)):
        libwdb.mk_arb4(self.db_fp, name, cta.doubles(points, double_count=12))

    @mk_wrap_primitive(primitives.Primitive)
    def arb5(self, name, points=(1, 1, 0, 1, -1, 0, -1, -1, 0, -1, 1, 0, 0, 0, 1)):
        libwdb.mk_arb5(self.db_fp, name, cta.doubles(points, double_count=15))

    @mk_wrap_primitive(primitives.Primitive)
    def arb6(self, name, points=(1, 1, 0, 1, -1, 0, -1, -1, 0, -1, 1, 0, 1, 0, 1, -1, 0, 1)):
        libwdb.mk_arb6(self.db_fp, name, cta.doubles(points, double_count=18))

    @mk_wrap_primitive(primitives.Primitive)
    def arb7(self, name, points=(1, 1, -1, 1, -1, -1, -3, -1, -1, -1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 1)):
        libwdb.mk_arb7(self.db_fp, name, cta.doubles(points, double_count=21))

    @mk_wrap_primitive(primitives.ARB8)
    def arb8(self, name, points=(1, 1, -1, 1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1)):
        libwdb.mk_arb8(self.db_fp, name, cta.doubles(points, double_count=24))

    @mk_wrap_primitive(primitives.Ellipsoid)
    def ellipsoid(self, name, center=(0, 0, 0), a=(1, 0, 0), b=(0, 1, 0), c=(0, 0, 1)):
        libwdb.mk_ell(self.db_fp, name, cta.point(center), cta.direction(a), cta.direction(b), cta.direction(c))

    @mk_wrap_primitive(primitives.Torus)
    def torus(self, name, center=(0, 0, 0), n=(0, 0, 1), r_revolution=1, r_cross=0.2):
        libwdb.mk_tor(self.db_fp, name, cta.point(center), cta.direction(n), r_revolution, r_cross)

    @mk_wrap_primitive(primitives.RCC)
    def rcc(self, name, base=(0, 0, 0), height=(0, 0, 1), radius=1):
        libwdb.mk_rcc(self.db_fp, name, cta.point(base), cta.direction(height), radius)

    @mk_wrap_primitive(primitives.TGC)
    def tgc(self, name, base=(0, 0, 0), height=(0, 0, 1), a=(0, 1, 0), b=(0.5, 0, 0), c=(0, 0.5, 0), d=(1, 0, 0)):
        libwdb.mk_tgc(self.db_fp, name, cta.point(base), cta.direction(height),
                      cta.direction(a), cta.direction(b), cta.direction(c), cta.direction(d))

    @mk_wrap_primitive(primitives.Cone)
    def cone(self, name, base=(0, 0, 0), n=(0, 0, 1), h=1, r_base=1, r_top=0.5):
        libwdb.mk_cone(self.db_fp, name, cta.point(base), cta.direction(n), h, r_base, r_top)

    @mk_wrap_primitive(primitives.TRC)
    def trc(self, name, base=(0, 0, 0), height=(0, 0, 1), r_base=1, r_top=0.5):
        libwdb.mk_trc_h(self.db_fp, name, cta.point(base), cta.direction(height), r_base, r_top)

    @mk_wrap_primitive(primitives.VOL)
    def vol(self, name, file_name, x_dim=1, y_dim=1, z_dim=1, low_thresh=0, high_thresh=128, cell_size=(1, 1, 1),
            mat=Transform.unit()):
        libwdb.mk_vol(self.db_fp, name, file_name, x_dim, y_dim, z_dim, low_thresh, high_thresh,
                      cta.point(cell_size), cta.transform(mat))

    @mk_wrap_primitive(primitives.EBM)
    def ebm(self, name, file_name, x_dim=350, y_dim=350, tallness=20, mat=Transform.unit()):
        libwdb.mk_ebm(self.db_fp, name, file_name, x_dim, y_dim, tallness, cta.transform(mat))

    @mk_wrap_primitive(primitives.ARS)
    def ars(self, name, ncurves, pts_per_curve, curves):
        mod_curves  = [[None for x in range(pts_per_curve*3)] for y in range(ncurves)]
        ## for start
        for i in range(pts_per_curve):
            for j in range(3):
                mod_curves[0][3*i+j] = curves[0][j]
        ##for other curves
        for i in range(1,ncurves-1):
            for j in range(3*pts_per_curve):
                mod_curves[i][j] = curves[i][j]
        ## for end
        for i in range(pts_per_curve):
            for j in range(3):
                mod_curves[ncurves-1][3*i+j] = curves[ncurves-1][j]

        libwdb.mk_ars(self.db_fp, name, ncurves, pts_per_curve, cta.array2d(mod_curves, use_brlcad_malloc=True))

    @mk_wrap_primitive(primitives.BOT)
    def bot(self, name, mode=1, orientation=1, flags=0, vertices=([0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0]),
                 faces = ([0, 1, 2], [1, 2, 3], [3, 1, 0]), thickness=(), face_mode=()):
        #Todo : Add Plates
        if mode == 3:
            raise BRLCADException("Plates not implemented")
        libwdb.mk_bot(self.db_fp, name, mode, orientation, flags, len(vertices), len(faces), cta.doubles(vertices),
                      cta.integers(faces), cta.doubles(thickness), 0)

    @mk_wrap_primitive(primitives.Superell)
    def superell(self, name, center=(0, 0, 0), a=(1, 0, 0), b=(0, 1, 0), c=(0, 0, 1), n=0, e=0):
        s = cta.brlcad_new(libwdb.struct_rt_superell_internal)
        s.magic = libwdb.RT_SUPERELL_INTERNAL_MAGIC
        s.v = cta.point(center)
        s.a = cta.point(a)
        s.b = cta.point(b)
        s.c = cta.point(c)
        s.e = e
        s.n = n
        libwdb.wdb_export(self.db_fp, name, libwdb.byref(s), libwdb.ID_SUPERELL, 1)

    @mk_wrap_primitive(primitives.Half)
    def half(self, name, norm=(1, 0, 0), d=1.0):
        libwdb.mk_half(self.db_fp, name, cta.point(norm), d)

    @mk_wrap_primitive(primitives.RPC)
    def rpc(self, name, base=(0, 0, 0), height=(-1, 0, 0), breadth=(0, 0, 1), half_width=0.5):
        libwdb.mk_rpc(self.db_fp, name, cta.point(base), cta.direction(height), cta.direction(breadth), half_width)

    @mk_wrap_primitive(primitives.RHC)
    def rhc(self, name, base=(0, 0, 0), height=(-1, 0, 0), breadth=(0, 0, 1), half_width=0.5, asymptote=0.1):
            libwdb.mk_rhc(self.db_fp, name, cta.point(base), cta.direction(height),
                          cta.direction(breadth), half_width, asymptote)

    @mk_wrap_primitive(primitives.EPA)
    def epa(self, name, base=(0, 0, 0), height=(0, 0, 1), n_major=(0, 1, 0), r_major=1, r_minor=0.5):
        libwdb.mk_epa(self.db_fp, name, cta.point(base), cta.direction(height), cta.direction(n_major), r_major, r_minor)

    @mk_wrap_primitive(primitives.EHY)
    def ehy(self, name, base=(0, 0, 0), height=(0, 0, 1), n_major=(0, 1, 0), r_major=1, r_minor=0.5, asymptote=0.1):
        libwdb.mk_ehy(self.db_fp, name, cta.point(base), cta.direction(height),
                      cta.direction(n_major), r_major, r_minor, asymptote)

    @mk_wrap_primitive(primitives.Hyperboloid)
    def hyperboloid(self, name, base=(0, 0, 0), height=(0, 0, 1), a_vec=(0, 1, 0), b_mag=0.5, base_neck_ratio=0.2):
        libwdb.mk_hyp(self.db_fp, name, cta.point(base), cta.direction(height),
                      cta.direction(a_vec), b_mag, base_neck_ratio)

    @mk_wrap_primitive(primitives.ETO)
    def eto(self, name, center=(0, 0, 0), n=(0, 0, 1), s_major=(0, 0.5, 0.5), r_revolution=1, r_minor=0.2):
        libwdb.mk_eto(self.db_fp, name, cta.point(center), cta.direction(n),
                      cta.direction(s_major), r_revolution, r_minor)

    @mk_wrap_primitive(primitives.ARBN)
    def arbn(self, name, planes=(1, 0, 0, 1, -1, 0, 0, 1, 0, 1, 0, 1, 0, -1, 0, 1, 0, 0, 1, 1, 0, 0, -1, 1)):
        # mk_arbn will free the passed array, so we need to alloc the memory in brlcad code:
        # TODO: this was fixed in the latest BRL-CAD code, need to do it conditionally on version ?
        planes_arg = cta.brlcad_copy(cta.planes(planes), "mk_arbn")
        libwdb.mk_arbn(self.db_fp, name, len(planes_arg)/4, planes_arg)

    @mk_wrap_primitive(primitives.Particle)
    def particle(self, name, base=(0, 0, 0), height=(0, 0, 1), r_base=0.5, r_end=0.2):
        libwdb.mk_particle(self.db_fp, name, cta.point(base), cta.direction(height), r_base, r_end)

    @mk_wrap_primitive(primitives.Grip)
    def grip(self, name, center=(0, 0, 0), normal=(1, 0, 0), magnitude=1):
        libwdb.mk_grip(self.db_fp, name, cta.point(center, 3), cta.point(normal, 3), magnitude)

    @mk_wrap_primitive(primitives.Pipe)
    def pipe(self, name, points=(((0, 0, 0), 0.5, 0.3, 1), ((0, 0, 1), 0.5, 0.3, 1))):
        """
        The pipe points are: (point, outer_d, inner_d, bend_d)
        """
        seg_list = libwdb.bu_list_new()
        libwdb.mk_pipe_init(seg_list)
        for pipe_point in points:
            libwdb.mk_add_pipe_pt(seg_list, cta.point(pipe_point[0]), *pipe_point[1:])
        libwdb.mk_pipe(self.db_fp, name, seg_list)

    @mk_wrap_primitive(primitives.Metaball)
    def metaball(self, name, points=(((1, 1, 1), 1, 0), ((0, 0, 1), 2, 0)), threshold=1, method=2):
        """
        ctrl_points: corresponds to metaball control points
               ctrl_point = (point, field_strength, sweat)
        """
        libwdb.mk_metaball(self.db_fp, name, len(points), method, threshold, cta.array2d_fixed_cols(points, 5,
                                                                                                use_brlcad_malloc=True))

    @mk_wrap_primitive(primitives.Sketch)
    def sketch(self, name, sketch=None):
        if not sketch:
            sketch = primitives.Sketch(name)
        si = libwdb.struct_rt_sketch_internal()
        si.magic = libwdb.RT_SKETCH_INTERNAL_MAGIC
        si.V = cta.point(sketch.base)
        si.u_vec = cta.point(sketch.u_vec)
        si.v_vec = cta.point(sketch.v_vec)
        si.curve, vertices = sketch.build_curves()
        si.vert_count = len(vertices)
        si.verts = cta.points2D(vertices, point_count=len(vertices))
        libwdb.mk_sketch(self.db_fp, name, libwdb.byref(si))

    @mk_wrap_primitive(primitives.Extrude)
    def extrude(self, name, sketch=None, base=None, height=None, u_vec=None, v_vec=None):
        libwdb.mk_extrusion(
            self.db_fp, name, sketch.name,
            cta.point((0, 0, 0) if base is None else base),
            cta.point((0, 0, 1) if height is None else height),
            cta.point((1, 0, 0) if u_vec is None else u_vec),
            cta.point((0, 1, 0) if v_vec is None else v_vec),
            0
        )

    @mk_wrap_primitive(primitives.Revolve)
    def revolve(self, name, sketch=None, revolve_center=None, revolve_axis=None, radius=None, angle=None):
        ri = cta.brlcad_new(libwdb.struct_rt_revolve_internal)
        ri.magic = libwdb.RT_REVOLVE_INTERNAL_MAGIC
        ri.v3d = cta.point((0, 0, 0) if revolve_center is None else revolve_center)
        ri.axis3d = cta.point((0, 0, 1) if revolve_axis is None else revolve_axis)
        ri.r = cta.point((1, 0, 0) if radius is None else radius)
        ri.ang = 180 if angle is None else angle
        ri.sketch_name = cta.str_to_vls(sketch.name)
        libwdb.wdb_export(self.db_fp, name, libwdb.byref(ri), libwdb.ID_REVOLVE, 1)

    @mk_wrap_primitive(primitives.Combination)
    def combination(self, name, is_region=False, tree=None, inherit=False,
                    shader=None, material=None, rgb_color=None, temperature=0,
                    region_id=0, air_code=0, gift_material=0, line_of_sight=0,
                    is_fastgen=libwdb.REGION_NON_FASTGEN):
        if not tree:
            raise ValueError("Empty tree for combination: {0}".format(name))
        tree = primitives.wrap_tree(tree)
        new_comb = cta.brlcad_new(libwdb.struct_rt_comb_internal)
        new_comb.magic = libwdb.RT_COMB_MAGIC
        new_comb.tree = tree.build_tree()
        new_comb.region_flag = cta.bool_to_char(is_region)
        new_comb.is_fastgen = cta.int_to_char(is_fastgen)
        new_comb.region_id = region_id
        new_comb.aircode = air_code
        new_comb.GIFTmater = gift_material
        new_comb.los = line_of_sight
        new_comb.rgb_valid = cta.bool_to_char(rgb_color)
        new_comb.rgb = cta.rgb(rgb_color)
        new_comb.temperature = temperature
        new_comb.shader = cta.str_to_vls(shader)
        new_comb.material = cta.str_to_vls(material)
        new_comb.inherit = cta.bool_to_char(inherit)
        libwdb.wdb_export(self.db_fp, name, libwdb.byref(new_comb), libwdb.ID_COMBINATION, 1)

    def region(self, *args, **kwargs):
        kwargs["is_region"] = True
        return self.combination(*args, **kwargs)

    def hole(self, hole_start=None, hole_depth=None, hole_radius=None, obj_list=None):
        """
        Makes a hole in the given object list (which all need to be combinations).
        It creates an RCC with the given parameters, and modifies each combination
        by replacing the original combination tree with subtract(original - hole_rcc).
        The only new object added is the hole RCC which will be named "make_hole_X"
        where X is some integer.
        """
        check_missing_params(
            "WDB.hole", hole_start=hole_start, hole_depth=hole_depth, hole_radius=hole_radius, obj_list=obj_list
        )
        if isinstance(obj_list, str):
            obj_list = [obj_list]
        idb_types, db_internals, dpp_list = zip(*[self._lookup_internal(obj) for obj in obj_list])
        if not idb_types:
            raise ValueError("No objects to hole !")
        if any(map(lambda idb_type: idb_type != libwdb.ID_COMBINATION, idb_types)):
            raise ValueError("All shapes should be combinations: {}".format(obj_list))
        dir_list = cta.ctypes_array(dpp_list)
        libwdb.make_hole(
            self.db_fp,
            cta.point(hole_start),
            cta.point(hole_depth),
            hole_radius,
            len(dpp_list), dir_list
        )

    def save(self, shape):
        if SAVE_MAP.has_key(shape.__class__):
            SAVE_MAP[shape.__class__](self, shape)
        else:
            raise NotImplementedError("Save not implemented for type: {0}".format(type(shape)))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
