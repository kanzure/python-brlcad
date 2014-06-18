"""
Wraps the BRL-CAD GED library with python syntax.
"""
import brlcad._bindings.libged as libged
from brlcad.exceptions import BRLCADException
import brlcad.ctypes_adaptors as cta
import re
try:
    import readline
except ImportError:
    # readline is not available on windows:
    readline = None


class DBType(object):
    DB = "db"
    FILE = "file"
    DISK = "disk"
    DISK_APPEND = "disk_append"
    INMEM = "inmem"
    INMEM_APPEND = "inmem_append"


_GED_INSTANCE = None

# These commands should not be auto-wrapped because thy have already been
# implemented in this file as ged_open and ged_close.
_OTHER_COMMANDS = [
    "ged_open",
    "ged_close",
]

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

def _construct_ged_commands(other_commands=_OTHER_COMMANDS):
    """
    Update the GED class with the additional functions based on libged.
    Anything in libged is fair game, with the exception of the commands listed
    in the other_commands list.

    :param other_commands: commands to exclude from creating new functions for
    :type other_commands: list of strings
    """
    for libgedkey in libged.__dict__.keys():
        # skip any unnamed functions
        if len(libgedkey) < len("ged_") + 1:
            continue

        if libgedkey.startswith("ged_") and libgedkey not in other_commands:
            # grab the wrapped function
            libgedfunction = libged.__getattribute__(libgedkey)

            # create a new function
            def some_ged_command(self, *args):
                return self.execute_command(libgedfunction, *args)

            # apply the wrapper
            some_ged_command = ged_command(some_ged_command)

            # apply it to the GED object, but remove "ged_" from the start
            setattr(GED, libgedkey[4:], some_ged_command)

_construct_ged_commands()
