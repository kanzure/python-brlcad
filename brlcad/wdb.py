"""
Python wrapper for libwdb adapting python types to the needed ctypes structures.
"""

import brlcad._bindings.libwdb as libwdb
import os
from ctypes_adaptors import ct_points, ct_direction, ct_planes, ct_transform, ct_rgb, ct_bool
from exceptions import BRLCADException
from primitives.table import create_primitive

# This is unfortunately needed because the original signature
# has an array of doubles and ctpyes refuses to take None as value for that
libwdb.mk_addmember.argtypes = [libwdb.String, libwdb.POINTER(libwdb.struct_bu_list), libwdb.POINTER(libwdb.c_double), libwdb.c_int]

def brlcad_copy(obj, debug_msg):
    """
    Returns a copy of the obj using a buffer allocated via bu_malloc.
    This is needed when BRLCAD frees the memory pointed to by the passed in pointer - yes that happens !
    """
    count = libwdb.sizeof(obj)
    obj_copy = libwdb.bu_malloc(count, debug_msg)
    libwdb.memmove(obj_copy, libwdb.addressof(obj), count)
    return type(obj).from_address(obj_copy)

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

    def lookup_internal(self, name):
        db_internal = libwdb.rt_db_internal()
        dpp = libwdb.pointer(libwdb.POINTER(libwdb.directory)())
        idb_type = libwdb.rt_db_lookup_internal(
            self.db_ip, name,
            dpp,
            libwdb.byref(db_internal),
            libwdb.LOOKUP_NOISY,
            libwdb.byref(libwdb.rt_uniresource)
        )
        if not idb_type:
            return None
        return create_primitive(idb_type, db_internal, dpp.contents.contents)

    def close(self):
        libwdb.wdb_close(self.db_fp)

    def sphere(self, name, center, radius):
        libwdb.mk_sph(self.db_fp, name, ct_points(center), radius)

    def rpp(self, name, pmin, pmax):
        libwdb.mk_rpp(self.db_fp, name, ct_points(pmin), ct_points(pmax))

    def wedge(self, name, vertex, x_dir, z_dir, x_len, y_len, z_len, x_top_len):
        libwdb.mk_wedge(self.db_fp, name,
                     ct_points(vertex), ct_direction(x_dir), ct_direction(z_dir),
                     x_len, y_len, z_len, x_top_len)

    def arb4(self, name, points):
        libwdb.mk_arb4(self.db_fp, name, ct_points(points, point_count=4))

    def arb5(self, name, points):
        libwdb.mk_arb5(self.db_fp, name, ct_points(points, point_count=5))

    def arb6(self, name, points):
        libwdb.mk_arb6(self.db_fp, name, ct_points(points, point_count=6))

    def arb7(self, name, points):
        libwdb.mk_arb7(self.db_fp, name, ct_points(points, point_count=7))

    def arb8(self, name, points):
        libwdb.mk_arb8(self.db_fp, name, ct_points(points, point_count=8))

    def ellipsoid(self, name, center, a, b, c):
        libwdb.mk_ell(self.db_fp, name, ct_points(center), ct_direction(a), ct_direction(b), ct_direction(c))

    def torus(self, name, center, n, r_revolution, r_cross):
        libwdb.mk_tor(self.db_fp, name, ct_points(center), ct_direction(n), r_revolution, r_cross)

    def rcc(self, name, base, height, radius):
        libwdb.mk_rcc(self.db_fp, name, ct_points(base), ct_direction(height), radius)

    def tgc(self, name, base, height, a, b, c, d):
        libwdb.mk_tgc(self.db_fp, name, ct_points(base), ct_direction(height),
                   ct_direction(a), ct_direction(b), ct_direction(c), ct_direction(d))

    def cone(self, name, base, n, h, r_base, r_top):
        libwdb.mk_cone(self.db_fp, name, ct_points(base), ct_direction(n), h, r_base, r_top)

    def trc(self, name, base, height, r_base, r_top):
        libwdb.mk_trc_h(self.db_fp, name, ct_points(base), ct_direction(height), r_base, r_top)

    def trc_top(self, name, base, top, r_base, r_top):
        libwdb.mk_trc_top(self.db_fp, name, ct_points(base), ct_direction(top), r_base, r_top)

    def rpc(self, name, base, height, breadth, half_width):
        libwdb.mk_rpc(self.db_fp, name, ct_points(base), ct_direction(height), ct_direction(breadth), half_width)

    def rhc(self, name, base, height, breadth, half_width, asymptote):
        libwdb.mk_rhc(self.db_fp, name, ct_points(base), ct_direction(height), ct_direction(breadth), half_width, asymptote)

    def epa(self, name, base, height, n_major, r_major, r_minor):
        libwdb.mk_epa(self.db_fp, name, ct_points(base), ct_direction(height), ct_direction(n_major), r_major, r_minor)

    def ehy(self, name, base, height, n_major, r_major, r_minor, asymptote):
        libwdb.mk_ehy(self.db_fp, name, ct_points(base), ct_direction(height), ct_direction(n_major), r_major, r_minor, asymptote)

    def hyperboloid(self, name, base, height, a_vec, b_mag, base_neck_ratio):
        libwdb.mk_hyp(self.db_fp, name, ct_points(base), ct_direction(height), ct_direction(a_vec), b_mag, base_neck_ratio)

    def eto(self, name, center, n, s_major, r_revolution, r_minor):
        libwdb.mk_eto(self.db_fp, name, ct_points(center), ct_direction(n), ct_direction(s_major), r_revolution, r_minor)

    def arbn(self, name, planes):
        # mk_arbn will free the passed array, so we need to alloc the memory in brlcad code:
        # TODO: this was fixed in the latest BRL-CAD code, need to do it conditionally on version ?
        planes_arg = brlcad_copy(ct_planes(planes), "mk_arbn")
        libwdb.mk_arbn(self.db_fp, name, len(planes), planes_arg)

    def particle(self, name, base, v_end, r_base, r_end):
        libwdb.mk_particle(self.db_fp, name, ct_points(base), ct_direction(v_end), r_base, r_end)

    def pipe(self, name, segments):
        seg_list = libwdb.bu_list_new()
        libwdb.mk_pipe_init(seg_list)
        for segment in segments:
            libwdb.mk_add_pipe_pt(seg_list, ct_points(segment[0]), *segment[1:])
        libwdb.mk_pipe(self.db_fp, name, seg_list)

    def combine(self, name, members, inherit=False, append_ok=False):
        self._make_comb(name, members, 0, shader_name=None,
                        shader_params=None, rgb_color=None,
                        region_id=0, air_code=0, material=0, line_of_sight=0,
                        inherit=inherit, append_ok=append_ok, gift_semantics=False )

    def region(self, name, members, shader_name, shader_params,
               rgb_color, region_id, air_code=0, material=0, line_of_sight=0,
               inherit=False, append_ok=False, gift_semantics=False):
        self._make_comb(name, members, 1, shader_name=shader_name,
                        shader_params=shader_params, rgb_color=rgb_color,
                        region_id=region_id, air_code=air_code, material=material, line_of_sight=line_of_sight,
                        inherit=inherit, append_ok=append_ok, gift_semantics=gift_semantics )

    def _make_comb(self, name, members, region_kind, shader_name,
                   shader_params, rgb_color, region_id, air_code,
                   material, line_of_sight, inherit, append_ok, gift_semantics):
        if not members:
            return
        member_list = libwdb.bu_list_new()
        if isinstance(members, str):
            members = [members]
        for member in members:
            if isinstance(member, str):
                operation = ord('u')
                matrix = None
            else:
                operation = ord(member[1])
                matrix = ct_transform(member[2]) if len(member) > 2 else None
                member = member[0]
            libwdb.mk_addmember(member, member_list, matrix, operation)
        libwdb.mk_comb(self.db_fp, name, member_list, region_kind, shader_name, shader_params,
                    ct_rgb(rgb_color), region_id, air_code,
                    material, line_of_sight, ct_bool(inherit), ct_bool(append_ok), ct_bool(gift_semantics))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
