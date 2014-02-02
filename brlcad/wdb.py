"""
Python wrapper for libwdb adapting python types to the needed ctypes structures.
"""

from ctypes_adaptors import *
import brlcad._bindings.libwdb as wdb

# This is unfortunately needed because the original signature
# has an array of doubles and ctpyes refuses to take None as value for that
wdb.mk_addmember.argtypes = [wdb.String, wdb.POINTER(wdb.struct_bu_list), wdb.POINTER(wdb.c_double), wdb.c_int]

def brlcad_copy(obj, debug_msg):
    """
    Returns a copy of the obj using a buffer allocated via bu_malloc.
    This is needed when BRLCAD frees the memory pointed to by the passed in pointer - yes that happens !
    """
    count = wdb.sizeof(obj)
    obj_copy = wdb.bu_malloc(count, debug_msg)
    wdb.memmove(obj_copy, wdb.addressof(obj), count)
    return type(obj).from_address(obj_copy)

class WDB:
    """
    Object to create a write-only BRLCad data base file and populate it.
    """
    
    def __init__(self, db_file, title):
        try:
            self.db_fp = wdb.wdb_fopen(db_file)
            wdb.mk_id(self.db_fp, title)
        except Exception as e:
            raise BRLCADException("Can't create DB file <{0}>: {1}".format(db_file, e))

    def close(self):
        wdb.wdb_close(self.db_fp)

    def sphere(self, name, center, radius):
        wdb.mk_sph(self.db_fp, name, ct_points(center), radius)

    def rpp(self, name, pmin, pmax):
        wdb.mk_rpp(self.db_fp, name, ct_points(pmin), ct_points(pmax))

    def wedge(self, name, vertex, x_dir, z_dir, x_len, y_len, z_len, x_top_len):
        wdb.mk_wedge(self.db_fp, name,
                     ct_points(vertex), ct_direction(x_dir), ct_direction(z_dir),
                     x_len, y_len, z_len, x_top_len)

    def arb4(self, name, points):
        wdb.mk_arb4(self.db_fp, name, ct_points(points, point_count=4))

    def arb5(self, name, points):
        wdb.mk_arb5(self.db_fp, name, ct_points(points, point_count=5))

    def arb6(self, name, points):
        wdb.mk_arb6(self.db_fp, name, ct_points(points, point_count=6))

    def arb7(self, name, points):
        wdb.mk_arb7(self.db_fp, name, ct_points(points, point_count=7))

    def arb8(self, name, points):
        wdb.mk_arb8(self.db_fp, name, ct_points(points, point_count=8))

    def ellipsoid(self, name, center, a, b, c):
        wdb.mk_ell(self.db_fp, name, ct_points(center), ct_direction(a), ct_direction(b), ct_direction(c))

    def torus(self, name, center, n, r_revolution, r_cross):
        wdb.mk_tor(self.db_fp, name, ct_points(center), ct_direction(n), r_revolution, r_cross)

    def rcc(self, name, base, height, radius):
        wdb.mk_rcc(self.db_fp, name, ct_points(base), ct_direction(height), radius)

    def tgc(self, name, base, height, a, b, c, d):
        wdb.mk_tgc(self.db_fp, name, ct_points(base), ct_direction(height),
                   ct_direction(a), ct_direction(b), ct_direction(c), ct_direction(d))

    def cone(self, name, base, n, h, r_base, r_top):
        wdb.mk_cone(self.db_fp, name, ct_points(base), ct_direction(n), h, r_base, r_top)

    def trc(self, name, base, height, r_base, r_top):
        wdb.mk_trc_h(self.db_fp, name, ct_points(base), ct_direction(height), r_base, r_top)

    def trc_top(self, name, base, top, r_base, r_top):
        wdb.mk_trc_top(self.db_fp, name, ct_points(base), ct_direction(top), r_base, r_top)

    def rpc(self, name, base, height, breadth, half_width):
        wdb.mk_rpc(self.db_fp, name, ct_points(base), ct_direction(height), ct_direction(breadth), half_width)

    def rhc(self, name, base, height, breadth, half_width, asymptote):
        wdb.mk_rhc(self.db_fp, name, ct_points(base), ct_direction(height), ct_direction(breadth), half_width, asymptote)

    def epa(self, name, base, height, n_major, r_major, r_minor):
        wdb.mk_epa(self.db_fp, name, ct_points(base), ct_direction(height), ct_direction(n_major), r_major, r_minor)

    def ehy(self, name, base, height, n_major, r_major, r_minor, asymptote):
        wdb.mk_ehy(self.db_fp, name, ct_points(base), ct_direction(height), ct_direction(n_major), r_major, r_minor, asymptote)

    def hyperboloid(self, name, base, height, a_vec, b_mag, base_neck_ratio):
        wdb.mk_hyp(self.db_fp, name, ct_points(base), ct_direction(height), ct_direction(a_vec), b_mag, base_neck_ratio)

    def eto(self, name, center, n, s_major, r_revolution, r_minor):
        wdb.mk_eto(self.db_fp, name, ct_points(center), ct_direction(n), ct_direction(s_major), r_revolution, r_minor)

    def arbn(self, name, planes):
        # mk_arbn will free the passed array, so we need to alloc the memory in brlcad code:
        planes_arg = brlcad_copy(ct_planes(planes), "mk_arbn")
        wdb.mk_arbn(self.db_fp, name, len(planes), planes_arg)

    def particle(self, name, base, v_end, r_base, r_end):
        wdb.mk_particle(self.db_fp, name, ct_points(base), ct_direction(v_end), r_base, r_end)

    def pipe(self, name, segments):
        seg_list = wdb.bu_list_new()
        wdb.mk_pipe_init(seg_list)
        for segment in segments:
            wdb.mk_add_pipe_pt(seg_list, ct_points(segment[0]), *segment[1:])
        wdb.mk_pipe(self.db_fp, name, seg_list)

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
        member_list = wdb.bu_list_new()
        for member in members:
            matrix = ct_transform(member[2]) if len(member) > 2 else None
            wdb.mk_addmember(member[0], member_list, matrix, ord(member[1]))
        wdb.mk_comb(self.db_fp, name, member_list, region_kind, shader_name, shader_params,
                    ct_rgb(rgb_color), region_id, air_code,
                    material, line_of_sight, ct_bool(inherit), ct_bool(append_ok), ct_bool(gift_semantics))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
