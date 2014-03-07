"""
Wraps the BRL-CAD GED library with python syntax.
"""
import brlcad._bindings.libged as libged
from brlcad.exceptions import BRLCADException
import brlcad.ctypes_adaptors as cta
import functools
import re
try:
    import readline
except ImportError:
    readline = None


class DBType(object):
    DB = "db"
    FILE = "file"
    DISK = "disk"
    DISK_APPEND = "disk_append"
    INMEM = "inmem"
    INMEM_APPEND = "inmem_append"


_GED_INSTANCE = None


def _execute_ged_command(ged_func, *args, **kwargs):
    if not _GED_INSTANCE:
        raise BRLCADException("GED is not yet open !")
    ged_func(_GED_INSTANCE, *args, **kwargs)


# TODO: investigate setting up automatically commands found in libged
# todo: investigate setting up doc strings from the BRL-CAD sources for the functions
#       perhaps it would make sense to include the help strings in the library ?
def ged_command(ged_func):
    """
    This decoration loads the GED commands in the package name space.
    Just decorate each GED command you want to show up in the package
    namespace with it, all the rest is automatically done.
    """
    def global_func(*args, **kwargs):
        _execute_ged_command(ged_func, *args, **kwargs)
    # this will make the help(command) work:
    global_func.__doc__ = ged_func.__doc__
    global_func.__name__ = ged_func.__name__
    globals()[ged_func.__name__] = global_func
    return ged_func


def ged_open(file_name, dbtype=DBType.DB, existing_only=True):
    global _GED_INSTANCE
    ged_pointer = GED(file_name, dbtype=dbtype, existing_only=existing_only)
    if not ged_pointer:
        raise BRLCADException("Failed opening {}".format(file_name))
    if _GED_INSTANCE:
        old_instance = _GED_INSTANCE
        _GED_INSTANCE = None
        try:
            old_instance.close()
        except:
            ged_pointer.close()
            raise BRLCADException("Error closing open GED: {}".format(old_instance.file_name))
    _GED_INSTANCE = ged_pointer


def ged_close():
    global _GED_INSTANCE
    try:
        _GED_INSTANCE.close()
    finally:
        _GED_INSTANCE = None


class GED(object):
    """
    Wraps the ged structure of BRL-CAD.
    You can use it like this:

    from brlcad.ged import *
    with GED("file_name.g"):
        ls()

    This will assure the file is closed at the end, but it's not optimal for interactive use,
    for that you can use:

    ged_open("file_name.g")
    ls('-l')
    ged_close()

    Beware that this version will close first whatever other DB was open !

    """
    def __init__(self, file_name, dbtype=DBType.DB, existing_only=True):
        self.file_name = file_name
        result = libged.ged_open(dbtype, file_name, cta.bool(existing_only))
        if not result:
            raise BRLCADException("Error creating GED !")
        self._ged_pointer = result

    def __enter__(self):
        global _GED_INSTANCE
        self.old_ged_instance = _GED_INSTANCE
        _GED_INSTANCE = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _GED_INSTANCE
        _GED_INSTANCE = self.old_ged_instance
        self.close()

    def execute_command(self, ged_function, *args, **kwargs):
        args = list(args)
        command_name = kwargs.get("command_name", ged_function.__name__)
        args.insert(0, command_name)
        if readline:
            history_index = readline.get_current_history_length()
        while True:
            cmd_args = cta.ctypes_string_array(args)
            result = ged_function(self._ged_pointer, len(cmd_args), cmd_args)
            # if result != libged.GED_OK:
            #     print "Result: <", result, ">"
            if not (result & libged.GED_MORE):
                break
            prompt = self._ged_pointer.contents.ged_result_str.contents.vls_str
            new_input = raw_input(prompt)
            args.extend(new_input.split())
        if readline:
            # this code collapses the multiple history items resulting from
            # the "raw_input" calls to a single history item (same behavior as mged)
            new_history_index = readline.get_current_history_length()
            if new_history_index > history_index:
                command_pattern = re.compile("^(.*)\([^)]*\)\s*")
                command_matcher = command_pattern.search(readline.get_history_item(history_index))
                if command_matcher:
                    history_command = command_matcher.group(1)
                else:
                    history_command = ged_function.__name__
                crt_index = readline.get_current_history_length()
                while crt_index > history_index:
                    readline.remove_history_item(history_index)
                    crt_index = readline.get_current_history_length()
                cmd_line = "{}(\"{}\")".format(
                    history_command, "\", \"".join(args[1:])
                )
                readline.add_history(cmd_line)
        if result & libged.GED_QUIET:
            ged_output = None
        else:
            ged_output = self._ged_pointer.contents.ged_result_str.contents.vls_str
        if ged_output:
            print ged_output
        return result

    @ged_command
    def ls(self, *args):
        return self.execute_command(libged.ged_ls, *args)

    @ged_command
    def close(self, *args):
        return libged.ged_close(self._ged_pointer)

    @ged_command
    def ged_3ptarb(self, *args):
        return self.execute_command(libged.ged_3ptarb, *args, command_name="3ptarb")

    @ged_command
    def ged_in(self, *args):
        return self.execute_command(libged.ged_in, *args, command_name="in")

#*********** TODO: implement explicit list of params ? *******************#
    @ged_command
    def E(self, *args):
        return self.execute_command(libged.ged_E, *args)

    @ged_command
    def adc(self, *args):
        return self.execute_command(libged.ged_adc, *args)

    @ged_command
    def add_metaballpt(self, *args):
        return self.execute_command(libged.ged_add_metaballpt, *args)

    @ged_command
    def adjust(self, *args):
        return self.execute_command(libged.ged_adjust, *args)

    @ged_command
    def ae2dir(self, *args):
        return self.execute_command(libged.ged_ae2dir, *args)

    @ged_command
    def aet(self, *args):
        return self.execute_command(libged.ged_aet, *args)

    @ged_command
    def analyze(self, *args):
        return self.execute_command(libged.ged_analyze, *args)

    @ged_command
    def annotate(self, *args):
        return self.execute_command(libged.ged_annotate, *args)

    @ged_command
    def append_pipept(self, *args):
        return self.execute_command(libged.ged_append_pipept, *args)

    @ged_command
    def arb(self, *args):
        return self.execute_command(libged.ged_arb, *args)

    @ged_command
    def arced(self, *args):
        return self.execute_command(libged.ged_arced, *args)

    @ged_command
    def arot(self, *args):
        return self.execute_command(libged.ged_arot, *args)

    @ged_command
    def attr(self, *args):
        return self.execute_command(libged.ged_attr, *args)

    @ged_command
    def autoview(self, *args):
        return self.execute_command(libged.ged_autoview, *args)

    @ged_command
    def bb(self, *args):
        return self.execute_command(libged.ged_bb, *args)

    @ged_command
    def bev(self, *args):
        return self.execute_command(libged.ged_bev, *args)

    @ged_command
    def blast(self, *args):
        return self.execute_command(libged.ged_blast, *args)

    @ged_command
    def bo(self, *args):
        return self.execute_command(libged.ged_bo, *args)

    @ged_command
    def bot(self, *args):
        return self.execute_command(libged.ged_bot, *args)

    @ged_command
    def bot_condense(self, *args):
        return self.execute_command(libged.ged_bot_condense, *args)

    @ged_command
    def bot_decimate(self, *args):
        return self.execute_command(libged.ged_bot_decimate, *args)

    @ged_command
    def bot_dump(self, *args):
        return self.execute_command(libged.ged_bot_dump, *args)

    @ged_command
    def bot_edge_split(self, *args):
        return self.execute_command(libged.ged_bot_edge_split, *args)

    @ged_command
    def bot_face_fuse(self, *args):
        return self.execute_command(libged.ged_bot_face_fuse, *args)

    @ged_command
    def bot_face_sort(self, *args):
        return self.execute_command(libged.ged_bot_face_sort, *args)

    @ged_command
    def bot_face_split(self, *args):
        return self.execute_command(libged.ged_bot_face_split, *args)

    @ged_command
    def bot_flip(self, *args):
        return self.execute_command(libged.ged_bot_flip, *args)

    @ged_command
    def bot_fuse(self, *args):
        return self.execute_command(libged.ged_bot_fuse, *args)

    @ged_command
    def bot_merge(self, *args):
        return self.execute_command(libged.ged_bot_merge, *args)

    @ged_command
    def bot_smooth(self, *args):
        return self.execute_command(libged.ged_bot_smooth, *args)

    @ged_command
    def bot_split(self, *args):
        return self.execute_command(libged.ged_bot_split, *args)

    @ged_command
    def bot_sync(self, *args):
        return self.execute_command(libged.ged_bot_sync, *args)

    @ged_command
    def bot_vertex_fuse(self, *args):
        return self.execute_command(libged.ged_bot_vertex_fuse, *args)

    @ged_command
    def brep(self, *args):
        return self.execute_command(libged.ged_brep, *args)

    @ged_command
    def cat(self, *args):
        return self.execute_command(libged.ged_cat, *args)

    @ged_command
    def cc(self, *args):
        return self.execute_command(libged.ged_cc, *args)

    @ged_command
    def center(self, *args):
        return self.execute_command(libged.ged_center, *args)

    @ged_command
    def clone(self, *args):
        return self.execute_command(libged.ged_clone, *args)

    @ged_command
    def coil(self, *args):
        return self.execute_command(libged.ged_coil, *args)

    @ged_command
    def color(self, *args):
        return self.execute_command(libged.ged_color, *args)

    @ged_command
    def comb(self, *args):
        return self.execute_command(libged.ged_comb, *args)

    @ged_command
    def comb_color(self, *args):
        return self.execute_command(libged.ged_comb_color, *args)

    @ged_command
    def comb_std(self, *args):
        return self.execute_command(libged.ged_comb_std, *args)

    @ged_command
    def combmem(self, *args):
        return self.execute_command(libged.ged_combmem, *args)

    @ged_command
    def concat(self, *args):
        return self.execute_command(libged.ged_concat, *args)

    @ged_command
    def constraint(self, *args):
        return self.execute_command(libged.ged_constraint, *args)

    @ged_command
    def copy(self, *args):
        return self.execute_command(libged.ged_copy, *args)

    @ged_command
    def copyeval(self, *args):
        return self.execute_command(libged.ged_copyeval, *args)

    @ged_command
    def copymat(self, *args):
        return self.execute_command(libged.ged_copymat, *args)

    @ged_command
    def cpi(self, *args):
        return self.execute_command(libged.ged_cpi, *args)

    @ged_command
    def dbip(self, *args):
        return self.execute_command(libged.ged_dbip, *args)

    @ged_command
    def dbot_dump(self, *args):
        return self.execute_command(libged.ged_dbot_dump, *args)

    @ged_command
    def debugbu(self, *args):
        return self.execute_command(libged.ged_debugbu, *args)

    @ged_command
    def debugdir(self, *args):
        return self.execute_command(libged.ged_debugdir, *args)

    @ged_command
    def debuglib(self, *args):
        return self.execute_command(libged.ged_debuglib, *args)

    @ged_command
    def debugmem(self, *args):
        return self.execute_command(libged.ged_debugmem, *args)

    @ged_command
    def debugnmg(self, *args):
        return self.execute_command(libged.ged_debugnmg, *args)

    @ged_command
    def decompose(self, *args):
        return self.execute_command(libged.ged_decompose, *args)

    @ged_command
    def delay(self, *args):
        return self.execute_command(libged.ged_delay, *args)

    @ged_command
    def delete_metaballpt(self, *args):
        return self.execute_command(libged.ged_delete_metaballpt, *args)

    @ged_command
    def delete_pipept(self, *args):
        return self.execute_command(libged.ged_delete_pipept, *args)

    @ged_command
    def dir2ae(self, *args):
        return self.execute_command(libged.ged_dir2ae, *args)

    @ged_command
    def draw(self, *args):
        return self.execute_command(libged.ged_draw, *args)

    @ged_command
    def dump(self, *args):
        return self.execute_command(libged.ged_dump, *args)

    @ged_command
    def dup(self, *args):
        return self.execute_command(libged.ged_dup, *args)

    @ged_command
    def eac(self, *args):
        return self.execute_command(libged.ged_eac, *args)

    @ged_command
    def echo(self, *args):
        return self.execute_command(libged.ged_echo, *args)

    @ged_command
    def edarb(self, *args):
        return self.execute_command(libged.ged_edarb, *args)

    @ged_command
    def edcodes(self, *args):
        return self.execute_command(libged.ged_edcodes, *args)

    @ged_command
    def edcolor(self, *args):
        return self.execute_command(libged.ged_edcolor, *args)

    @ged_command
    def edcomb(self, *args):
        return self.execute_command(libged.ged_edcomb, *args)

    @ged_command
    def edit(self, *args):
        return self.execute_command(libged.ged_edit, *args)

    @ged_command
    def editit(self, *args):
        return self.execute_command(libged.ged_editit, *args)

    @ged_command
    def edmater(self, *args):
        return self.execute_command(libged.ged_edmater, *args)

    @ged_command
    def erase(self, *args):
        return self.execute_command(libged.ged_erase, *args)

    @ged_command
    def ev(self, *args):
        return self.execute_command(libged.ged_ev, *args)

    @ged_command
    def exists(self, *args):
        return self.execute_command(libged.ged_exists, *args)

    @ged_command
    def expand(self, *args):
        return self.execute_command(libged.ged_expand, *args)

    @ged_command
    def eye(self, *args):
        return self.execute_command(libged.ged_eye, *args)

    @ged_command
    def eye_pos(self, *args):
        return self.execute_command(libged.ged_eye_pos, *args)

    @ged_command
    def facetize(self, *args):
        return self.execute_command(libged.ged_facetize, *args)

    @ged_command
    def fb2pix(self, *args):
        return self.execute_command(libged.ged_fb2pix, *args)

    @ged_command
    def find(self, *args):
        return self.execute_command(libged.ged_find, *args)

    @ged_command
    def find_arb_edge_nearest_pt(self, *args):
        return self.execute_command(libged.ged_find_arb_edge_nearest_pt, *args)

    @ged_command
    def find_bot_edge_nearest_pt(self, *args):
        return self.execute_command(libged.ged_find_bot_edge_nearest_pt, *args)

    @ged_command
    def find_botpt_nearest_pt(self, *args):
        return self.execute_command(libged.ged_find_botpt_nearest_pt, *args)

    @ged_command
    def find_metaballpt_nearest_pt(self, *args):
        return self.execute_command(libged.ged_find_metaballpt_nearest_pt, *args)

    @ged_command
    def find_pipept_nearest_pt(self, *args):
        return self.execute_command(libged.ged_find_pipept_nearest_pt, *args)

    @ged_command
    def form(self, *args):
        return self.execute_command(libged.ged_form, *args)

    @ged_command
    def fracture(self, *args):
        return self.execute_command(libged.ged_fracture, *args)

    @ged_command
    def gdiff(self, *args):
        return self.execute_command(libged.ged_gdiff, *args)

    @ged_command
    def get(self, *args):
        return self.execute_command(libged.ged_get, *args)

    @ged_command
    def get_autoview(self, *args):
        return self.execute_command(libged.ged_get_autoview, *args)

    @ged_command
    def get_bot_edges(self, *args):
        return self.execute_command(libged.ged_get_bot_edges, *args)

    @ged_command
    def get_comb(self, *args):
        return self.execute_command(libged.ged_get_comb, *args)

    @ged_command
    def get_eyemodel(self, *args):
        return self.execute_command(libged.ged_get_eyemodel, *args)

    @ged_command
    def get_type(self, *args):
        return self.execute_command(libged.ged_get_type, *args)

    @ged_command
    def glob(self, *args):
        return self.execute_command(libged.ged_glob, *args)

    @ged_command
    def gqa(self, *args):
        return self.execute_command(libged.ged_gqa, *args)

    @ged_command
    def graph(self, *args):
        return self.execute_command(libged.ged_graph, *args)

    @ged_command
    def grid(self, *args):
        return self.execute_command(libged.ged_grid, *args)

    @ged_command
    def grid2model_lu(self, *args):
        return self.execute_command(libged.ged_grid2model_lu, *args)

    @ged_command
    def grid2view_lu(self, *args):
        return self.execute_command(libged.ged_grid2view_lu, *args)

    @ged_command
    def group(self, *args):
        return self.execute_command(libged.ged_group, *args)

    @ged_command
    def hide(self, *args):
        return self.execute_command(libged.ged_hide, *args)

    @ged_command
    def how(self, *args):
        return self.execute_command(libged.ged_how, *args)

    @ged_command
    def human(self, *args):
        return self.execute_command(libged.ged_human, *args)

    @ged_command
    def illum(self, *args):
        return self.execute_command(libged.ged_illum, *args)

    @ged_command
    def importFg4Section(self, *args):
        return self.execute_command(libged.ged_importFg4Section, *args)

    @ged_command
    def inside(self, *args):
        return self.execute_command(libged.ged_inside, *args)

    @ged_command
    def instance(self, *args):
        return self.execute_command(libged.ged_instance, *args)

    @ged_command
    def isize(self, *args):
        return self.execute_command(libged.ged_isize, *args)

    @ged_command
    def item(self, *args):
        return self.execute_command(libged.ged_item, *args)

    @ged_command
    def joint(self, *args):
        return self.execute_command(libged.ged_joint, *args)

    @ged_command
    def keep(self, *args):
        return self.execute_command(libged.ged_keep, *args)

    @ged_command
    def keypoint(self, *args):
        return self.execute_command(libged.ged_keypoint, *args)

    @ged_command
    def kill(self, *args):
        return self.execute_command(libged.ged_kill, *args)

    @ged_command
    def killall(self, *args):
        return self.execute_command(libged.ged_killall, *args)

    @ged_command
    def killrefs(self, *args):
        return self.execute_command(libged.ged_killrefs, *args)

    @ged_command
    def killtree(self, *args):
        return self.execute_command(libged.ged_killtree, *args)

    @ged_command
    def ged_ged_list(self, *args):
        return self.execute_command(libged.ged_list, *args)

    @ged_command
    def loadview(self, *args):
        return self.execute_command(libged.ged_loadview, *args)

    @ged_command
    def lod(self, *args):
        return self.execute_command(libged.ged_lod, *args)

    @ged_command
    def log(self, *args):
        return self.execute_command(libged.ged_log, *args)

    @ged_command
    def lookat(self, *args):
        return self.execute_command(libged.ged_lookat, *args)

    @ged_command
    def lt(self, *args):
        return self.execute_command(libged.ged_lt, *args)

    @ged_command
    def m2v_point(self, *args):
        return self.execute_command(libged.ged_m2v_point, *args)

    @ged_command
    def make(self, *args):
        return self.execute_command(libged.ged_make, *args)

    @ged_command
    def make_bb(self, *args):
        return self.execute_command(libged.ged_make_bb, *args)

    @ged_command
    def make_name(self, *args):
        return self.execute_command(libged.ged_make_name, *args)

    @ged_command
    def make_pnts(self, *args):
        return self.execute_command(libged.ged_make_pnts, *args)

    @ged_command
    def ged_ged_match(self, *args):
        return self.execute_command(libged.ged_match, *args)

    @ged_command
    def mater(self, *args):
        return self.execute_command(libged.ged_mater, *args)

    @ged_command
    def memprint(self, *args):
        return self.execute_command(libged.ged_memprint, *args)

    @ged_command
    def mirror(self, *args):
        return self.execute_command(libged.ged_mirror, *args)

    @ged_command
    def model2grid_lu(self, *args):
        return self.execute_command(libged.ged_model2grid_lu, *args)

    @ged_command
    def model2view(self, *args):
        return self.execute_command(libged.ged_model2view, *args)

    @ged_command
    def model2view_lu(self, *args):
        return self.execute_command(libged.ged_model2view_lu, *args)

    @ged_command
    def move(self, *args):
        return self.execute_command(libged.ged_move, *args)

    @ged_command
    def move_all(self, *args):
        return self.execute_command(libged.ged_move_all, *args)

    @ged_command
    def move_arb_edge(self, *args):
        return self.execute_command(libged.ged_move_arb_edge, *args)

    @ged_command
    def move_arb_face(self, *args):
        return self.execute_command(libged.ged_move_arb_face, *args)

    @ged_command
    def move_botpt(self, *args):
        return self.execute_command(libged.ged_move_botpt, *args)

    @ged_command
    def move_botpts(self, *args):
        return self.execute_command(libged.ged_move_botpts, *args)

    @ged_command
    def move_metaballpt(self, *args):
        return self.execute_command(libged.ged_move_metaballpt, *args)

    @ged_command
    def move_pipept(self, *args):
        return self.execute_command(libged.ged_move_pipept, *args)

    @ged_command
    def mrot(self, *args):
        return self.execute_command(libged.ged_mrot, *args)

    @ged_command
    def nirt(self, *args):
        return self.execute_command(libged.ged_nirt, *args)

    @ged_command
    def nmg_collapse(self, *args):
        return self.execute_command(libged.ged_nmg_collapse, *args)

    @ged_command
    def nmg_fix_normals(self, *args):
        return self.execute_command(libged.ged_nmg_fix_normals, *args)

    @ged_command
    def nmg_simplify(self, *args):
        return self.execute_command(libged.ged_nmg_simplify, *args)

    @ged_command
    def ocenter(self, *args):
        return self.execute_command(libged.ged_ocenter, *args)

    @ged_command
    def orient(self, *args):
        return self.execute_command(libged.ged_orient, *args)

    @ged_command
    def orotate(self, *args):
        return self.execute_command(libged.ged_orotate, *args)

    @ged_command
    def oscale(self, *args):
        return self.execute_command(libged.ged_oscale, *args)

    @ged_command
    def otranslate(self, *args):
        return self.execute_command(libged.ged_otranslate, *args)

    @ged_command
    def overlay(self, *args):
        return self.execute_command(libged.ged_overlay, *args)

    @ged_command
    def pathlist(self, *args):
        return self.execute_command(libged.ged_pathlist, *args)

    @ged_command
    def pathsum(self, *args):
        return self.execute_command(libged.ged_pathsum, *args)

    @ged_command
    def perspective(self, *args):
        return self.execute_command(libged.ged_perspective, *args)

    @ged_command
    def pix2fb(self, *args):
        return self.execute_command(libged.ged_pix2fb, *args)

    @ged_command
    def plot(self, *args):
        return self.execute_command(libged.ged_plot, *args)

    @ged_command
    def pmat(self, *args):
        return self.execute_command(libged.ged_pmat, *args)

    @ged_command
    def pmodel2view(self, *args):
        return self.execute_command(libged.ged_pmodel2view, *args)

    @ged_command
    def png(self, *args):
        return self.execute_command(libged.ged_png, *args)

    @ged_command
    def polybinout(self, *args):
        return self.execute_command(libged.ged_polybinout, *args)

    @ged_command
    def pov(self, *args):
        return self.execute_command(libged.ged_pov, *args)

    @ged_command
    def prcolor(self, *args):
        return self.execute_command(libged.ged_prcolor, *args)

    @ged_command
    def prefix(self, *args):
        return self.execute_command(libged.ged_prefix, *args)

    @ged_command
    def prepend_pipept(self, *args):
        return self.execute_command(libged.ged_prepend_pipept, *args)

    @ged_command
    def preview(self, *args):
        return self.execute_command(libged.ged_preview, *args)

    @ged_command
    def protate(self, *args):
        return self.execute_command(libged.ged_protate, *args)

    @ged_command
    def ps(self, *args):
        return self.execute_command(libged.ged_ps, *args)

    @ged_command
    def pscale(self, *args):
        return self.execute_command(libged.ged_pscale, *args)

    @ged_command
    def pset(self, *args):
        return self.execute_command(libged.ged_pset, *args)

    @ged_command
    def ptranslate(self, *args):
        return self.execute_command(libged.ged_ptranslate, *args)

    @ged_command
    def pull(self, *args):
        return self.execute_command(libged.ged_pull, *args)

    @ged_command
    def push(self, *args):
        return self.execute_command(libged.ged_push, *args)

    @ged_command
    def put(self, *args):
        return self.execute_command(libged.ged_put, *args)

    @ged_command
    def put_comb(self, *args):
        return self.execute_command(libged.ged_put_comb, *args)

    @ged_command
    def putmat(self, *args):
        return self.execute_command(libged.ged_putmat, *args)

    @ged_command
    def qray(self, *args):
        return self.execute_command(libged.ged_qray, *args)

    @ged_command
    def quat(self, *args):
        return self.execute_command(libged.ged_quat, *args)

    @ged_command
    def qvrot(self, *args):
        return self.execute_command(libged.ged_qvrot, *args)

    @ged_command
    def rcodes(self, *args):
        return self.execute_command(libged.ged_rcodes, *args)

    @ged_command
    def rect(self, *args):
        return self.execute_command(libged.ged_rect, *args)

    @ged_command
    def red(self, *args):
        return self.execute_command(libged.ged_red, *args)

    @ged_command
    def redraw(self, *args):
        return self.execute_command(libged.ged_redraw, *args)

    @ged_command
    def regdef(self, *args):
        return self.execute_command(libged.ged_regdef, *args)

    @ged_command
    def region(self, *args):
        return self.execute_command(libged.ged_region, *args)

    @ged_command
    def remove(self, *args):
        return self.execute_command(libged.ged_remove, *args)

    @ged_command
    def reopen(self, *args):
        return self.execute_command(libged.ged_reopen, *args)

    @ged_command
    def report(self, *args):
        return self.execute_command(libged.ged_report, *args)

    @ged_command
    def rfarb(self, *args):
        return self.execute_command(libged.ged_rfarb, *args)

    @ged_command
    def rmap(self, *args):
        return self.execute_command(libged.ged_rmap, *args)

    @ged_command
    def rmat(self, *args):
        return self.execute_command(libged.ged_rmat, *args)

    @ged_command
    def rmater(self, *args):
        return self.execute_command(libged.ged_rmater, *args)

    @ged_command
    def rot(self, *args):
        return self.execute_command(libged.ged_rot, *args)

    @ged_command
    def rot_point(self, *args):
        return self.execute_command(libged.ged_rot_point, *args)

    @ged_command
    def rotate_about(self, *args):
        return self.execute_command(libged.ged_rotate_about, *args)

    @ged_command
    def rotate_arb_face(self, *args):
        return self.execute_command(libged.ged_rotate_arb_face, *args)

    @ged_command
    def rrt(self, *args):
        return self.execute_command(libged.ged_rrt, *args)

    @ged_command
    def rselect(self, *args):
        return self.execute_command(libged.ged_rselect, *args)

    @ged_command
    def rt(self, *args):
        return self.execute_command(libged.ged_rt, *args)

    @ged_command
    def rtabort(self, *args):
        return self.execute_command(libged.ged_rtabort, *args)

    @ged_command
    def rtcheck(self, *args):
        return self.execute_command(libged.ged_rtcheck, *args)

    @ged_command
    def rtwizard(self, *args):
        return self.execute_command(libged.ged_rtwizard, *args)

    @ged_command
    def savekey(self, *args):
        return self.execute_command(libged.ged_savekey, *args)

    @ged_command
    def saveview(self, *args):
        return self.execute_command(libged.ged_saveview, *args)

    @ged_command
    def scale(self, *args):
        return self.execute_command(libged.ged_scale, *args)

    @ged_command
    def screen_grab(self, *args):
        return self.execute_command(libged.ged_screen_grab, *args)

    @ged_command
    def search(self, *args):
        return self.execute_command(libged.ged_search, *args)

    @ged_command
    def select(self, *args):
        return self.execute_command(libged.ged_select, *args)

    @ged_command
    def set_output_script(self, *args):
        return self.execute_command(libged.ged_set_output_script, *args)

    @ged_command
    def set_transparency(self, *args):
        return self.execute_command(libged.ged_set_transparency, *args)

    @ged_command
    def set_uplotOutputMode(self, *args):
        return self.execute_command(libged.ged_set_uplotOutputMode, *args)

    @ged_command
    def setview(self, *args):
        return self.execute_command(libged.ged_setview, *args)

    @ged_command
    def shaded_mode(self, *args):
        return self.execute_command(libged.ged_shaded_mode, *args)

    @ged_command
    def shader(self, *args):
        return self.execute_command(libged.ged_shader, *args)

    @ged_command
    def shells(self, *args):
        return self.execute_command(libged.ged_shells, *args)

    @ged_command
    def showmats(self, *args):
        return self.execute_command(libged.ged_showmats, *args)

    @ged_command
    def simulate(self, *args):
        return self.execute_command(libged.ged_simulate, *args)

    @ged_command
    def size(self, *args):
        return self.execute_command(libged.ged_size, *args)

    @ged_command
    def slew(self, *args):
        return self.execute_command(libged.ged_slew, *args)

    @ged_command
    def solids_on_ray(self, *args):
        return self.execute_command(libged.ged_solids_on_ray, *args)

    @ged_command
    def sphgroup(self, *args):
        return self.execute_command(libged.ged_sphgroup, *args)

    @ged_command
    def summary(self, *args):
        return self.execute_command(libged.ged_summary, *args)

    @ged_command
    def sync(self, *args):
        return self.execute_command(libged.ged_sync, *args)

    @ged_command
    def tables(self, *args):
        return self.execute_command(libged.ged_tables, *args)

    @ged_command
    def tire(self, *args):
        return self.execute_command(libged.ged_tire, *args)

    @ged_command
    def title(self, *args):
        return self.execute_command(libged.ged_title, *args)

    @ged_command
    def tol(self, *args):
        return self.execute_command(libged.ged_tol, *args)

    @ged_command
    def tops(self, *args):
        return self.execute_command(libged.ged_tops, *args)

    @ged_command
    def tra(self, *args):
        return self.execute_command(libged.ged_tra, *args)

    @ged_command
    def track(self, *args):
        return self.execute_command(libged.ged_track, *args)

    @ged_command
    def tree(self, *args):
        return self.execute_command(libged.ged_tree, *args)

    @ged_command
    def unhide(self, *args):
        return self.execute_command(libged.ged_unhide, *args)

    @ged_command
    def units(self, *args):
        return self.execute_command(libged.ged_units, *args)

    @ged_command
    def v2m_point(self, *args):
        return self.execute_command(libged.ged_v2m_point, *args)

    @ged_command
    def vdraw(self, *args):
        return self.execute_command(libged.ged_vdraw, *args)

    @ged_command
    def version(self, *args):
        return self.execute_command(libged.ged_version, *args)

    @ged_command
    def view2grid_lu(self, *args):
        return self.execute_command(libged.ged_view2grid_lu, *args)

    @ged_command
    def view2model(self, *args):
        return self.execute_command(libged.ged_view2model, *args)

    @ged_command
    def view2model_lu(self, *args):
        return self.execute_command(libged.ged_view2model_lu, *args)

    @ged_command
    def view2model_vec(self, *args):
        return self.execute_command(libged.ged_view2model_vec, *args)

    @ged_command
    def view_func(self, *args):
        return self.execute_command(libged.ged_view_func, *args)

    @ged_command
    def viewdir(self, *args):
        return self.execute_command(libged.ged_viewdir, *args)

    @ged_command
    def vnirt(self, *args):
        return self.execute_command(libged.ged_vnirt, *args)

    @ged_command
    def voxelize(self, *args):
        return self.execute_command(libged.ged_voxelize, *args)

    @ged_command
    def vrot(self, *args):
        return self.execute_command(libged.ged_vrot, *args)

    @ged_command
    def wcodes(self, *args):
        return self.execute_command(libged.ged_wcodes, *args)

    @ged_command
    def whatid(self, *args):
        return self.execute_command(libged.ged_whatid, *args)

    @ged_command
    def which(self, *args):
        return self.execute_command(libged.ged_which, *args)

    @ged_command
    def which_shader(self, *args):
        return self.execute_command(libged.ged_which_shader, *args)

    @ged_command
    def who(self, *args):
        return self.execute_command(libged.ged_who, *args)

    @ged_command
    def wmater(self, *args):
        return self.execute_command(libged.ged_wmater, *args)

    @ged_command
    def xpush(self, *args):
        return self.execute_command(libged.ged_xpush, *args)

    @ged_command
    def ypr(self, *args):
        return self.execute_command(libged.ged_ypr, *args)

    @ged_command
    def zap(self, *args):
        return self.execute_command(libged.ged_zap, *args)

    @ged_command
    def zoom(self, *args):
        return self.execute_command(libged.ged_zoom, *args)

#********************* TODO: wrap params ******************************#
    @ged_command
    def addToDisplay(self, *args):
        # todo: wrap params: struct ged *gedp, const char *name
        # return self.execute_command(libged.ged_addToDisplay, "addToDisplay", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def arot_args(self, *args):
        # todo: wrap params: struct ged *gedp, int argc, const char *argv[], mat_t rmat
        # return self.execute_command(libged.ged_arot_args, "arot_args", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def build_tops(self, *args):
        # todo: wrap params: struct ged *gedp, char **start, char **end
        # return self.execute_command(libged.ged_build_tops, "build_tops", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def calc_adc_a1(self, *args):
        # todo: wrap params: struct ged_view *gvp
        # return self.execute_command(libged.ged_calc_adc_a1, "calc_adc_a1", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def calc_adc_a2(self, *args):
        # todo: wrap params: struct ged_view *gvp
        # return self.execute_command(libged.ged_calc_adc_a2, "calc_adc_a2", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def calc_adc_dst(self, *args):
        # todo: wrap params: struct ged_view *gvp
        # return self.execute_command(libged.ged_calc_adc_dst, "calc_adc_dst", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def calc_adc_pos(self, *args):
        # todo: wrap params: struct ged_view *gvp
        # return self.execute_command(libged.ged_calc_adc_pos, "calc_adc_pos", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def clip(self, *args):
        # todo: wrap params: fastf_t *xp1, fastf_t *yp1, fastf_t *xp2, fastf_t *yp2
        # return self.execute_command(libged.ged_clip, "clip", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def clip_polygon(self, *args):
        # todo: wrap params: GedClipType op, ged_polygon *subj, ged_polygon *clip, fastf_t sf, matp_t model2view, matp_t view2model
        # return self.execute_command(libged.ged_clip_polygon, "clip_polygon", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def clip_polygons(self, *args):
        # todo: wrap params: GedClipType op, ged_polygons *subj, ged_polygons *clip, fastf_t sf, matp_t model2view, matp_t view2model
        # return self.execute_command(libged.ged_clip_polygons, "clip_polygons", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def color_soltab(self, *args):
        # todo: wrap params: struct bu_list *hdlp
        # return self.execute_command(libged.ged_color_soltab, "color_soltab", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def count_tops(self, *args):
        # todo: wrap params: struct ged *gedp
        # return self.execute_command(libged.ged_count_tops, "count_tops", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def dbcopy(self, *args):
        # todo: wrap params: struct ged *from_gedp, struct ged *to_gedp, const char *from, const char *to, int fflag
        # return self.execute_command(libged.ged_dbcopy, "dbcopy", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def deering_persp_mat(self, *args):
        # todo: wrap params: fastf_t *m, const fastf_t *l, const fastf_t *h, const fastf_t *eye
        # return self.execute_command(libged.ged_deering_persp_mat, "deering_persp_mat", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def erasePathFromDisplay(self, *args):
        # todo: wrap params: struct ged *gedp, const char *path, int allow_split
        # return self.execute_command(libged.ged_erasePathFromDisplay, "erasePathFromDisplay", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def export_polygon(self, *args):
        # todo: wrap params: struct ged *gedp, ged_data_polygon_state *gdpsp, size_t polygon_i, const char *sname
        # return self.execute_command(libged.ged_export_polygon, "export_polygon", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def find_polygon_area(self, *args):
        # todo: wrap params: ged_polygon *gpoly, fastf_t sf, matp_t model2view, fastf_t size
        # return self.execute_command(libged.ged_find_polygon_area, "find_polygon_area", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def free(self, *args):
        # todo: wrap params: struct ged *gedp
        # return self.execute_command(libged.ged_free, "free", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def get_object_selections(self, *args):
        # todo: wrap params: Args missing !
        # return self.execute_command(libged.ged_get_object_selections, "get_object_selections", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def get_selection_set(self, *args):
        # todo: wrap params: Args missing !
        # return self.execute_command(libged.ged_get_selection_set, "get_selection_set", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def import_polygon(self, *args):
        # todo: wrap params: struct ged *gedp, const char *sname
        # return self.execute_command(libged.ged_import_polygon, "import_polygon", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def inside_internal(self, *args):
        # todo: wrap params: struct ged *gedp, struct rt_db_internal *ip, int argc, const char *argv[], int arg, char *o_name
        # return self.execute_command(libged.ged_inside_internal, "inside_internal", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def mike_persp_mat(self, *args):
        # todo: wrap params: fastf_t *pmat, const fastf_t *eye
        # return self.execute_command(libged.ged_mike_persp_mat, "mike_persp_mat", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def path_validate(self, *args):
        # todo: wrap params: struct ged *gedp, const struct db_full_path * const path
        # return self.execute_command(libged.ged_path_validate, "path_validate", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def persp_mat(self, *args):
        # todo: wrap params: fastf_t *m, fastf_t fovy, fastf_t aspect, fastf_t near1, fastf_t far1, fastf_t backoff
        # return self.execute_command(libged.ged_persp_mat, "persp_mat", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def polygons_overlap(self, *args):
        # todo: wrap params: struct ged *gedp, ged_polygon *polyA, ged_polygon *polyB
        # return self.execute_command(libged.ged_polygons_overlap, "polygons_overlap", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def rot_args(self, *args):
        # todo: wrap params: struct ged *gedp, int argc, const char *argv[], char *coord, mat_t rmat
        # return self.execute_command(libged.ged_rot_args, "rot_args", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def scale_args(self, *args):
        # todo: wrap params: struct ged *gedp, int argc, const char *argv[], fastf_t *sf1, fastf_t *sf2, fastf_t *sf3
        # return self.execute_command(libged.ged_scale_args, "scale_args", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def snap_to_grid(self, *args):
        # todo: wrap params: struct ged *gedp, fastf_t *vx, fastf_t *vy
        # return self.execute_command(libged.ged_snap_to_grid, "snap_to_grid", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def tra_args(self, *args):
        # todo: wrap params: struct ged *gedp, int argc, const char *argv[], char *coord, vect_t tvec
        # return self.execute_command(libged.ged_tra_args, "tra_args", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def vclip(self, *args):
        # todo: wrap params: vect_t a, vect_t b, fastf_t *min, fastf_t *max
        # return self.execute_command(libged.ged_vclip, "vclip", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def view_init(self, *args):
        # todo: wrap params: struct ged_view *gvp
        # return self.execute_command(libged.ged_view_init, "view_init", *args)
        raise NotImplementedError("Not implemented yet !")

    @ged_command
    def view_update(self, *args):
        # todo: wrap params: struct ged_view *gvp
        # return self.execute_command(libged.ged_view_update, "view_update", *args)
        raise NotImplementedError("Not implemented yet !")
