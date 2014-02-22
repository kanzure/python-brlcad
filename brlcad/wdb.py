"""
Python wrapper for libwdb adapting python types to the needed ctypes structures.
"""
import brlcad._bindings.libwdb as libwdb
import os
import ctypes_adaptors as cta
from exceptions import BRLCADException
import primitives.table as p_table
import primitives

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
                if self.db_ip:
                    self.db_fp = libwdb.wdb_dbopen(self.db_ip, libwdb.RT_WDB_TYPE_DB_DISK)
                    if libwdb.db_dirbuild(self.db_ip) < 0:
                        raise BRLCADException("Can't read existing DB file: <{0}>".format(db_file))
            if not self.db_fp:
                self.db_fp = libwdb.wdb_fopen(db_file)
                self.db_ip = self.db_fp.contents.dbip
            if title:
                libwdb.mk_id(self.db_fp, title)
        except Exception as e:
            raise BRLCADException("Can't create DB file <{0}>: {1}".format(db_file, e))

    def __iter__(self):
        for i in range(0, libwdb.RT_DBNHASH):
            dp = self.db_ip.contents.dbi_Head[i]
            while dp:
                crt_dir = dp.contents
                yield crt_dir
                dp = crt_dir.d_forw

    def ls(self):
        return [str(x.d_namep) for x in self if not(x.d_flags & libwdb.RT_DIR_HIDDEN)]

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
        libwdb.mk_sph(self.db_fp, name, cta.points(center), radius)

    @mk_wrap_primitive(primitives.Primitive)
    def rpp(self, name, pmin=(-1, -1, -1), pmax=(1, 1, 1)):
        libwdb.mk_rpp(self.db_fp, name, cta.points(pmin), cta.points(pmax))

    @mk_wrap_primitive(primitives.Primitive)
    def wedge(self, name, vertex=(0, 0, 0), x_dir=(1, 0, 0), z_dir=(0, 0, 1),
              x_len=1, y_len=1, z_len=1, x_top_len=0.5):
        libwdb.mk_wedge(self.db_fp, name,
                        cta.points(vertex), cta.direction(x_dir), cta.direction(z_dir),
                        x_len, y_len, z_len, x_top_len)

    @mk_wrap_primitive(primitives.Primitive)
    def arb4(self, name, points=(0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1)):
        libwdb.mk_arb4(self.db_fp, name, cta.points(points, point_count=4))

    @mk_wrap_primitive(primitives.Primitive)
    def arb5(self, name, points=(1, 1, 0, 1, -1, 0, -1, -1, 0, -1, 1, 0, 0, 0, 1)):
        libwdb.mk_arb5(self.db_fp, name, cta.points(points, point_count=5))

    @mk_wrap_primitive(primitives.Primitive)
    def arb6(self, name, points=(1, 1, 0, 1, -1, 0, -1, -1, 0, -1, 1, 0, 1, 0, 1, -1, 0, 1)):
        libwdb.mk_arb6(self.db_fp, name, cta.points(points, point_count=6))

    @mk_wrap_primitive(primitives.Primitive)
    def arb7(self, name, points=(1, 1, -1, 1, -1, -1, -3, -1, -1, -1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 1)):
        libwdb.mk_arb7(self.db_fp, name, cta.points(points, point_count=7))

    @mk_wrap_primitive(primitives.ARB8)
    def arb8(self, name, points=(1, 1, -1, 1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1)):
        libwdb.mk_arb8(self.db_fp, name, cta.points(points, point_count=8))

    @mk_wrap_primitive(primitives.Ellipsoid)
    def ellipsoid(self, name, center=(0, 0, 0), a=(1, 0, 0), b=(0, 1, 0), c=(0, 0, 1)):
        libwdb.mk_ell(self.db_fp, name, cta.points(center), cta.direction(a), cta.direction(b), cta.direction(c))

    @mk_wrap_primitive(primitives.Torus)
    def torus(self, name, center=(0, 0, 0), n=(0, 0, 1), r_revolution=1, r_cross=0.2):
        libwdb.mk_tor(self.db_fp, name, cta.points(center), cta.direction(n), r_revolution, r_cross)

    @mk_wrap_primitive(primitives.RCC)
    def rcc(self, name, base=(0, 0, 0), height=(0, 0, 1), radius=1):
        libwdb.mk_rcc(self.db_fp, name, cta.points(base), cta.direction(height), radius)

    @mk_wrap_primitive(primitives.TGC)
    def tgc(self, name, base=(0, 0, 0), height=(0, 0, 1), a=(0, 1, 0), b=(0.5, 0, 0), c=(0, 0.5, 0), d=(1, 0, 0)):
        libwdb.mk_tgc(self.db_fp, name, cta.points(base), cta.direction(height),
                      cta.direction(a), cta.direction(b), cta.direction(c), cta.direction(d))

    @mk_wrap_primitive(primitives.Cone)
    def cone(self, name, base=(0, 0, 0), n=(0, 0, 1), h=1, r_base=1, r_top=0.5):
        libwdb.mk_cone(self.db_fp, name, cta.points(base), cta.direction(n), h, r_base, r_top)

    @mk_wrap_primitive(primitives.TRC)
    def trc(self, name, base=(0, 0, 0), height=(0, 0, 1), r_base=1, r_top=0.5):
        libwdb.mk_trc_h(self.db_fp, name, cta.points(base), cta.direction(height), r_base, r_top)

    @mk_wrap_primitive(primitives.RPC)
    def rpc(self, name, base=(0, 0, 0), height=(-1, 0, 0), breadth=(0, 0, 1), half_width=0.5):
        libwdb.mk_rpc(self.db_fp, name, cta.points(base), cta.direction(height), cta.direction(breadth), half_width)

    @mk_wrap_primitive(primitives.RHC)
    def rhc(self, name, base=(0, 0, 0), height=(-1, 0, 0), breadth=(0, 0, 1), half_width=0.5, asymptote=0.1):
            libwdb.mk_rhc(self.db_fp, name, cta.points(base), cta.direction(height),
                          cta.direction(breadth), half_width, asymptote)

    @mk_wrap_primitive(primitives.EPA)
    def epa(self, name, base=(0, 0, 0), height=(0, 0, 1), n_major=(0, 1, 0), r_major=1, r_minor=0.5):
        libwdb.mk_epa(self.db_fp, name, cta.points(base), cta.direction(height), cta.direction(n_major), r_major, r_minor)

    @mk_wrap_primitive(primitives.EHY)
    def ehy(self, name, base=(0, 0, 0), height=(0, 0, 1), n_major=(0, 1, 0), r_major=1, r_minor=0.5, asymptote=0.1):
        libwdb.mk_ehy(self.db_fp, name, cta.points(base), cta.direction(height),
                      cta.direction(n_major), r_major, r_minor, asymptote)

    @mk_wrap_primitive(primitives.Hyperboloid)
    def hyperboloid(self, name, base=(0, 0, 0), height=(0, 0, 1), a_vec=(0, 1, 0), b_mag=0.5, base_neck_ratio=0.2):
        libwdb.mk_hyp(self.db_fp, name, cta.points(base), cta.direction(height),
                      cta.direction(a_vec), b_mag, base_neck_ratio)

    @mk_wrap_primitive(primitives.ETO)
    def eto(self, name, center=(0, 0, 0), n=(0, 0, 1), s_major=(0, 0.5, 0.5), r_revolution=1, r_minor=0.2):
        libwdb.mk_eto(self.db_fp, name, cta.points(center), cta.direction(n),
                      cta.direction(s_major), r_revolution, r_minor)

    @mk_wrap_primitive(primitives.ARBN)
    def arbn(self, name, planes=(1, 0, 0, 1, -1, 0, 0, 1, 0, 1, 0, 1, 0, -1, 0, 1, 0, 0, 1, 1, 0, 0, -1, 1)):
        # mk_arbn will free the passed array, so we need to alloc the memory in brlcad code:
        # TODO: this was fixed in the latest BRL-CAD code, need to do it conditionally on version ?
        planes_arg = cta.brlcad_copy(cta.planes(planes), "mk_arbn")
        libwdb.mk_arbn(self.db_fp, name, len(planes_arg)/4, planes_arg)

    @mk_wrap_primitive(primitives.Particle)
    def particle(self, name, base=(0, 0, 0), height=(0, 0, 1), r_base=0.5, r_end=0.2):
        libwdb.mk_particle(self.db_fp, name, cta.points(base), cta.direction(height), r_base, r_end)

    @mk_wrap_primitive(primitives.Pipe)
    def pipe(self, name, points=(((0, 0, 0), 0.5, 0.3, 1), ((0, 0, 1), 0.5, 0.3, 1))):
        seg_list = libwdb.bu_list_new()
        libwdb.mk_pipe_init(seg_list)
        for pipe_point in points:
            libwdb.mk_add_pipe_pt(seg_list, cta.points(pipe_point[0]), *pipe_point[1:])
        libwdb.mk_pipe(self.db_fp, name, seg_list)

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
