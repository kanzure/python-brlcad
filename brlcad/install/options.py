"""
Utilities to look up the installed brlcad version(s)
and the configured library options.
Separated to make the integration to the existing code easier.
"""

import os
import copy
import re
import subprocess

from distutils.version import StrictVersion
from ConfigParser import ConfigParser

class SetupException(Exception):
    pass

def is_win():
    """
    Check if the system is Windows.
    """
    return sys.platform.startswith("win")

def get_brlcad_param(brlcad_config, param_name):
    """
    Executes brlcad-config with the given param name and returns the result as a string.
    It will also do necessary parsing/checking of the result.
    """
    result = subprocess.check_output([brlcad_config, "--" + param_name]).strip()
    if param_name == "libs":
        # the libs are a special format, extract a list of library names:
        result = result.rsplit(None, 1).pop().split(";")
    elif param_name in ["libdir","includedir","prefix"]:
        # these are dirs: check if they exist, raise exception if not
        if not os.access(result, os.R_OK):
            raise SetupException("Directory for <{0}> not found: {1}".format(param_name, result))
    elif param_name == "version":
        result = StrictVersion(result)
    return result

def read_version(include_dir):
    """
    Reads the brlcad version out of the brlcad_config.h file
    """
    config_file = os.path.join(include_dir, "brlcad", "brlcad_config.h")
    if not os.access(config_file, os.R_OK):
        config_file = os.path.join(include_dir, "brlcad_config.h")
    if not os.access(config_file, os.R_OK):
        return None
    pattern = re.compile("#define\\s+VERSION\\s*\"([^\"]*)\"")
    with open(config_file) as config_in:
        for line in config_in:
            match = pattern.match(line)
            if match:
                return StrictVersion(match.group(1))
    return None

def get_brlcad_config(brlcad_prefix, logger):
    """
    Get the configuration params of the brlcad installed at the given prefix.
    Will return a dict with the parameters set, or None if no brlcad
    installation was found at the given path prefix.
    If brlcad_prefix is None, it will use the system path to find the brlcad
    installation (on both linux and windows).
    On linux this method uses the brlcad-config shell script shipped with brl-cad
    to set up the returned dict (named here "result"). On windows it will test
    for the standard directories and will fail if it can't find them.
    The result dict is set up with the following mappings:
    * result["prefix"] -> brlcad base install directory (should be same as brlcad_prefix);
    * result["includedir"] -> brlcad headers include directory;
    * result["libdir"] -> brlcad libraries install directory;
    * result["version"] -> brlcad version (distutils.version.StrictVersion instance);
    """
    iswin = is_win()
    bin_subdir = 'bin'
    if not brlcad_prefix:
        valid_paths = [
            path for path in os.getenv("PATH").split(os.pathsep)
            if os.access(os.path.join(path,'brlcad-config'),os.R_OK)
               and (not iswin
                    or os.path.basename(path.rstrip('/')).lower() == 'bin')
        ]
        if not valid_paths:
            logger.debug("No brlcad found on PATH: {0}".format(os.getenv("PATH")))
            return None
        (brlcad_prefix, bin_subdir) = os.path.split(os.path.abspath(valid_paths[0].rstrip('/')))
    brlcad_config = os.path.join(brlcad_prefix, bin_subdir, 'brlcad-config')
    result = None
    if not iswin and os.access(brlcad_config, os.X_OK):
        try:
            result = {
                "prefix": get_brlcad_param(brlcad_config, 'prefix'),
                "includedir": get_brlcad_param(brlcad_config, 'includedir'),
                "libdir": get_brlcad_param(brlcad_config, 'libdir'),
                "version": get_brlcad_param(brlcad_config, 'version'),
            }
        except SetupException:
            # we only log this, it is not yet critical
            print "Failed running brlcad-config: {0}".format(repr(brlcad_config))
            logger.debug("Failed running brlcad-config: {0}".format(repr(brlcad_config)))
    if not result:
        # brlcad-config based setup failed, try standard directories
        include_dir = os.path.join(brlcad_prefix, 'include')
        lib_dir = os.path.join(brlcad_prefix, 'lib')
        version = read_version(include_dir)
        if version and os.path.isdir(include_dir) and os.path.isdir(lib_dir):
            result = {
                "prefix": brlcad_prefix,
                "includedir": include_dir,
                "libdir": lib_dir,
                "version": version,
            }
    return result

def load_config():
    config = ConfigParser()
    config.readfp(open('python-brlcad.cfg'))
    config.read(os.path.expanduser('~/.python-brlcad.cfg'))
    return config

def parse_csv_list(list_str):
    return [value.strip() for value in list_str.split(",") if value.strip()]

def expand_libraries(options):
    """
    Read and expand the library list configured in options.
    """
    alias_map = dict()
    options["alias-map"] = alias_map
    if not options.has_key("libraries"):
        return alias_map
    aliases = parse_csv_list(options["libraries"])
    options["alias-list"] = aliases
    alias_set = set(aliases)
    for alias in aliases:
        lib_name = options.get("{0}-lib-name".format(alias), "lib{0}".format(alias))
        module_name = options.get("{0}-module-name".format(alias), "brlcad._bindings.{0}".format(lib_name))
        lib_header = options.get("{0}-lib-header".format(alias), "{0}.h".format(alias))
        dependencies = parse_csv_list(options.get("{0}-dependencies".format(alias),''))
        dependency_set = set(dependencies)
        if not dependency_set <= alias_set:
            raise SetupException("Missing dependencies: {0} -> {1}".format(alias, dependency_set - alias_set))
        lib = {
            "alias": alias,
            "lib-name": lib_name,
            "module-name": module_name,
            "lib-header": lib_header,
            "dependencies": dependencies,
        }
        alias_map[alias] = lib
    return alias_map


def load_brlcad_config(config, logger):
    if not config.has_section('brlcad'):
        raise SetupException("Configuration has no [brlcad] section !")
    version_list = []
    defaults = dict(config.items("brlcad"))
    options = copy.deepcopy(defaults)
    options["section"] = "brlcad"
    expand_libraries(options, logger)
    version_list.append(options)
    brlcad_pattern = re.compile("brlcad.+")
    for section in config.sections():
        if brlcad_pattern.match(section):
            options = copy.deepcopy(defaults)
            options.update(config.items(section))
            options["section"] = section
            expand_libraries(options, logger)
            version_list.append(options)
    return version_list


def load_ctypesgen_options(config, brlcad_install_path):
    options = ctypesgencore.options.get_default_options()
    if config.has_section('ctypes-gen'):
        options.__dict__.update(cfg.items('ctypes-gen'))
    options.include_symbols = None
    options.exclude_symbols = None
    options.output_language = "python"
    options.header_template = None
    options.strip_build_path = None
    options.include_search_paths = ["{0}/include".format(brlcad_install_path)]

    options.inserted_files = []
    options.cpp = "gcc -E"
    options.save_preprocessed_headers = None

    options.other_headers = []
    options.compile_libdirs = []
    options.runtime_libdirs = []

    return options


