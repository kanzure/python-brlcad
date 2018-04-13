"""
Utilities to look up the installed brlcad version(s) and the configured library
options.
"""

import sys
import os
import copy
import re
import subprocess
import ctypesgencore

from distutils.version import StrictVersion
from ConfigParser import ConfigParser


class SetupException(Exception):
    pass


def is_win(platform=sys.platform):
    """
    Check if the system is Windows.
    """
    return platform.startswith("win")


def check_gcc(config, logger):
    paths = os.getenv("PATH").split(os.pathsep)
    gcc_exe = "gcc"
    if is_win() and config.has_section("gcc"):
        paths += [path.strip() for path in config.get("gcc", "win-path").split(os.pathsep)]
        os.environ["PATH"] += os.pathsep.join(paths)
        gcc_exe = "gcc.exe"
    if not "" in paths:
        paths.append("")
    errors = []
    for path in paths:
        gcc_bin = os.path.join(path, gcc_exe)
        try:
            version = subprocess.check_output([gcc_bin, "-dumpversion"])
            logger.debug("Found gcc: {0} -> {1}".format(gcc_bin, version))
            return gcc_bin, StrictVersion(version.strip())
        except (OSError, subprocess.CalledProcessError) as e:
            errors.append("Error checking gcc executable {0}: {1}".format(gcc_bin, e))
    for error in errors:
        logger.debug(error)
    raise SetupException("Couldn't find working gcc !")


def get_brlcad_param(brlcad_config, param_name):
    """
    Executes brlcad-config with the given param name and returns the result as a string.
    It will also do necessary parsing/checking of the result.
    """
    result = subprocess.check_output([brlcad_config, "--" + param_name]).strip()
    if param_name == "libs":
        # the libs are a special format, extract a list of library names:
        result = result.rsplit(None, 1).pop().split(";")
    elif param_name in ["libdir", "includedir", "prefix"]:
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


def check_brlcad_installation(brlcad_prefix, bin_subdir, logger):
    """
    Get the configuration params of the brlcad installed at the given prefix.
    Will return a dict with the parameters set, or None if no brlcad
    installation was found at the given path prefix.
    On linux this method uses the brlcad-config shell script shipped with brl-cad
    to set up the returned dict (named here "result"). On windows it will test
    for the standard directories and will fail if it can't find them.
    The result dict is set up with the following mappings:
    * result["prefix"] -> brlcad base install directory (should be same as brlcad_prefix);
    * result["includedir"] -> brlcad headers include directory;
    * result["libdir"] -> brlcad libraries install directory;
    * result["version"] -> brlcad version (distutils.version.StrictVersion instance);
    """
    bin_dir = os.path.join(brlcad_prefix, bin_subdir)
    brlcad_config = os.path.join(bin_dir, "brlcad-config")
    result = None
    if not is_win() and os.access(brlcad_config, os.X_OK):
        try:
            result = {
                "prefix": get_brlcad_param(brlcad_config, "prefix"),
                "includedir": get_brlcad_param(brlcad_config, "includedir"),
                "libdir": get_brlcad_param(brlcad_config, "libdir"),
                "bindir": bin_dir,
                "version": get_brlcad_param(brlcad_config, "version"),
            }
        except SetupException:
            # we only log this, it is not yet critical
            logger.debug("Failed running brlcad-config: {0}".format(repr(brlcad_config)))
    if not result:
        # brlcad-config based setup failed, try standard directories
        include_dir = os.path.join(brlcad_prefix, "include")
        lib_dir = os.path.join(brlcad_prefix, "lib")
        version = read_version(include_dir)
        if version and os.path.isdir(include_dir) and os.path.isdir(lib_dir):
            result = {
                "prefix": brlcad_prefix,
                "includedir": include_dir,
                "libdir": lib_dir,
                "bindir": bin_dir,
                "version": version,
            }
    return result


def find_brlcad_installations(config, logger):
    """
    Returns all brlcad installations which could be found.
    If the BRLCAD_PREFIX environment variable is set, only that prefix is
    checked (and the result list will be empty if there's no suitable brlcad
    installation found there).
    Otherwise the directories on the PATH environment variable are searched
    first, then the [brlcad*]/prefix settings in python-brlcad.cfg and
    ~/.python-brlcad.cfg are checked. All the valid versions found are returned
    in the result list.
    """
    # checking for BRLCAD_PREFIX
    prefix = os.getenv("BRLCAD_PREFIX", None)
    if prefix:
        brlcad_info = check_brlcad_installation(prefix, "bin", logger)
        return [brlcad_info] if brlcad_info else None
    # checking for brlcad installations on the PATH
    iswin = is_win()
    valid_paths = [
        path for path in os.getenv("PATH").split(os.pathsep)
        if os.access(os.path.join(path, "brlcad-config"), os.R_OK)
           and (not iswin
                or os.path.basename(path.rstrip("/")).lower() == "bin")
    ]
    prefixes = set()
    result = []
    if not valid_paths:
        logger.debug("No brlcad found on PATH: {0}".format(os.getenv("PATH")))
    else:
        for path in valid_paths:
            brlcad_prefix, bin_subdir = os.path.split(os.path.abspath(path))
            if not brlcad_prefix in prefixes:
                prefixes.add(brlcad_prefix)
                brlcad_info = check_brlcad_installation(brlcad_prefix, bin_subdir, logger)
                if brlcad_info:
                    result.append(brlcad_info)
                else:
                    logger.debug("No valid brlcad installation found at path: {0}".format(path))
    # checking for standard prefixes configured in python_brlcad.cfg
    brlcad_pattern = re.compile("brlcad.*")
    for section in config.sections():
        if brlcad_pattern.match(section) and config.has_option(section, "prefix"):
            prefix = config.get(section, "prefix")
            if not prefix in prefixes:
                prefixes.add(prefix)
                brlcad_info = check_brlcad_installation(prefix, "bin", logger)
                if brlcad_info:
                    result.append(brlcad_info)
                else:
                    logger.debug("No valid brlcad installation found at prefix: {0}".format(prefix))
    return result


def load_config():
    config = ConfigParser()
    config.readfp(open("python-brlcad.cfg"))
    config.read(os.path.join(os.path.expanduser("~"), ".python-brlcad.cfg"))
    return config


def parse_csv_list(list_str):
    return [value.strip() for value in list_str.split(",") if value.strip()]


def resolve_booleans(options):
    for key in options:
        value = options[key]
        if value == "True":
            options[key] = True
        elif value == "False":
            options[key] = False


def load_brlcad_options(config):
    if not config.has_section("brlcad"):
        raise SetupException("Configuration has no [brlcad] section !")
    version_list = []
    defaults = dict(config.items("brlcad"))
    options = copy.deepcopy(defaults)
    options["section"] = "brlcad"
    version_list.append(options)
    brlcad_pattern = re.compile("brlcad.+")
    for section in config.sections():
        if brlcad_pattern.match(section):
            options = copy.deepcopy(defaults)
            options.update(config.items(section))
            options["section"] = section
            version_list.insert(0, options)
    return version_list


def find_shared_lib_file(base_dirs, lib_name):
    for base_dir in base_dirs:
        base_path = os.path.join(base_dir, lib_name)
        for ext in [".so", ".dll", ".dylib"]:
            lib_path = base_path + ext
            if os.access(lib_path, os.R_OK):
                return lib_path
    raise SetupException("Missing shared library file: {0}".format(lib_name))


def norm_win_path(path, escape_spaces=False):
    """
    On windows we need to replace backslashes with forward slashes,
    otherwise ctypesgen will not work properly.
    """
    if is_win():
        path = re.sub(r"\\+", "/", path)
        if escape_spaces:
            path = '"' + path + '"'
    return path


def setup_libraries(bindings_path, config, settings, brlcad_info, logger):
    """
    Read and expand the library list configured in options.
    """
    default_options = ctypesgencore.options.get_default_options()
    default_options.include_symbols = None
    default_options.exclude_symbols = None
    default_options.output_language = "python"
    default_options.header_template = None
    default_options.strip_build_path = None
    default_options.save_preprocessed_headers = None
    default_options.cpp = None
    if config.has_section("ctypes-gen"):
        config_options = dict(config.items("ctypes-gen"))
        resolve_booleans(config_options)
        default_options.__dict__.update(config_options)
    default_options.inserted_files = []
    default_options.other_headers = []
    default_options.compile_libdirs = []
    default_options.runtime_libdirs = []
    if not default_options.cpp:
        gcc_bin, gcc_version = check_gcc(config, logger)
        default_options.cpp = gcc_bin + " -E"
    lib_dir = brlcad_info["libdir"]
    bin_dir = brlcad_info["bindir"]
    include_dir = brlcad_info["includedir"]
    default_options.include_search_paths = [
        norm_win_path(include_dir, escape_spaces=True),
        norm_win_path(os.path.join(include_dir, "brlcad"), escape_spaces=True),
    ]
    options_map = {}
    options_list = []
    aliases = parse_csv_list(settings.get("libraries", ""))
    alias_set = set(aliases)
    for alias in aliases:
        options = copy.deepcopy(default_options)
        options_list.append(options)
        lib_name = settings.get("{0}-lib-name".format(alias), "lib{0}".format(alias))
        options.brlcad_lib_alias = alias
        options.brlcad_lib_name = lib_name
        options_map[alias] = options
        lib_headers = parse_csv_list(settings.get("{0}-lib-headers".format(alias), "{0}.h".format(alias)))
        dependencies = parse_csv_list(settings.get("{0}-dependencies".format(alias), ""))
        options.include_symbols = settings.get("{0}-include-pattern".format(alias), options.include_symbols)
        dependency_set = set(dependencies)
        if not dependency_set <= alias_set:
            raise SetupException("Missing dependencies: {0} -> {1}".format(alias, dependency_set - alias_set))
        options.modules = [options_map[ln].brlcad_lib_name for ln in dependencies]
        options.output = os.path.join(bindings_path, "{0}.py".format(lib_name))
        lib_path = find_shared_lib_file([bin_dir, lib_dir], lib_name)
        options.libraries = [norm_win_path(lib_path)]
        for i in xrange(0, len(lib_headers)):
            lib_headers[i] = os.path.join(include_dir, "brlcad", lib_headers[i])
            if not os.access(lib_headers[i], os.R_OK):
                raise SetupException("Missing header file: {0}".format(lib_headers[i]))
        options.headers = lib_headers
    return options_list, options_map, brlcad_info


def match_brlcad_version(brlcad_options, brlcad_installations, logger):
    """
    Iterate the brlcad installations in the order found, and try to match it
    to a set of configuration options.
    """
    for version in brlcad_options:
        min_version = version.get("min-brlcad-version", None)
        if min_version:
            min_version = StrictVersion(min_version.strip())
        max_version = version.get("max-brlcad-version", None)
        if max_version:
            max_version = StrictVersion(max_version.strip())
        logger.debug("Checking {0}: {1} -> {2}".format(version["section"], min_version, max_version))
        for brlcad_info in brlcad_installations:
            if min_version and min_version > brlcad_info["version"]:
                continue
            if max_version and max_version < brlcad_info["version"]:
                continue
            logger.debug("Found matching brlcad installation: {0}".format(brlcad_info["prefix"]))
            yield version, brlcad_info


def load_ctypesgen_options(bindings_path, config, logger):
    """
    Looks up the ctypesgen options based on the available brlcad version(s) and
    configuration settings.
    The result is depending on:
    * PATH and BRLCAD_PATH environment variables;
    * python-brlcad.cfg and ~/.python-brlcad.cfg settings;
    * installed brlcad version(s) which could be found;
    * the OS you run on;
    In any case this method will try hard to find a working combination of
    ctypesgen options. In particular it will check each library for existence
    of headers and object files. It will also check for a working gcc.
    """
    brlcad_options = load_brlcad_options(config)
    brlcad_installations = find_brlcad_installations(config, logger)
    version_iter = match_brlcad_version(brlcad_options, brlcad_installations, logger)
    for version, brlcad_info in version_iter:
        try:
            return setup_libraries(bindings_path, config, version, brlcad_info, logger)
        except Exception as e:
            logger.debug("Failed checking brlcad installation: {0}".format(e))
    raise SetupException("Couldn't find a matching brlcad installation !")
