"""
The post_install script is the the beating heart of python-brlcad. After
setuptools runs the default install command, it runs the entrypoint ``main``
which generates the python/BRL-CAD bindings.

This needs to be a post-install script because on most python installations,
the setup script is executed with elevated permissons. After installation, such
as during the first run, the script has less than elevated permissions and
can't insert generated files into the installed location. So that's why this is
a part of the setuptools install process.
"""

import sys
import os
import json
import logging
import imp
import shutil
import glob

# used for configuraing ctypesgen options
import argparse

import ctypesgencore

def setup_logging(level=logging.DEBUG):
    """
    Dump everything to stdout by default.

    http://docs.python.org/2/howto/logging-cookbook.html
    """
    logger = logging.getLogger("brlcad_post_install")
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    return logger

def is_py32():
    """
    Tries really hard to determine if the current running version of python is
    32-bit python.
    """
    return sys.maxsize > 2**32

def is_win32():
    """
    Check if the system is Windows.
    """
    return sys.platform == "win32"

def generate_wrapper(libname, libpath, header_path, outputfile, logger, modules=[], other_known_names=[], debug=False):
    """
    Generate a ctypes wrapper around the library.

    @param libname: library name
    @param libpath: path to the shared library
    @param header_path: single header file to scan for symbols
    @param outputfile: location at which to dump python source code
    @param debug: toggle additional ctypesgen error/warning output
    """
    # setup an object on which i can store some attributes
    options = argparse.Namespace()

    options.output = outputfile
    options.libraries = [libpath]
    options.headers = [header_path]

    options.all_headers = False
    options.builtin_symbols = False
    options.include_macros = False
    options.include_symbols = None
    options.exclude_symbols = None
    options.no_python_types = True
    options.no_gnu_types = True
    options.no_stddef_types = True

    options.output_language = "python"

    options.show_all_errors = debug
    options.show_long_errors = debug
    options.show_macro_warnings = debug

    options.other_headers = []
    options.modules = modules
    options.compile_libdirs = []
    options.runtime_libdirs = []

    # At first glance this might seem like something that would cause
    # cross-platform compatibility issues. Somehow it doesn't.
    options.include_search_paths = ["/usr/brlcad/include"]

    options.header_template = None
    options.strip_build_path = None
    options.inserted_files = []

    options.other_known_names = other_known_names

    options.cpp = "gcc -E"
    options.save_preprocessed_headers = None

    # parse
    logger.debug("parsing")
    descriptions = ctypesgencore.parser.parse(options.headers, options)

    # process
    logger.debug("processing")
    ctypesgencore.processor.process(descriptions, options)

    # print
    logger.debug("printing")
    ctypesgencore.printer_python.WrapperPrinter(options.output, options, descriptions)

def cleanup_bindings_dir(bindings_path, logger):
    """
    Remove any leftover directories from a previous install.
    """

    try:
        # make the _bindings folder
        os.makedirs(bindings_path)
    except OSError as error:
        logger.debug("_bindings path already exists, deleting it")

        shutil.rmtree(bindings_path)

    # also remove _bindings from the local directory
    try:
        logger.debug("Deleting another _bindings/")
        shutil.rmtree(os.path.join(os.path.dirname(__file__), "_bindings"))
    except Exception as exception:
        logger.debug("Wasn't there, is okay.")

def main(library_path, logger=None):
    if not logger:
        logger = setup_logging()

    logger.debug("ctypesgencore version is {0}".format(ctypesgencore.__version__))

    # The actual list of brlcad libraries that are supported.
    argh_brlcad_library_names = list(set([
        "bu",
        "raytrace",
        "rt",
        "db5",
        "rtgeom",
        "analyze",
        "base",
        "bn",
        "brep",
        "wdb",
        "clipper",
        "cursor",
        "dm",
        "exppp",
        "express",
        "fb",
        "fft",
        "gcv",
        "nmg",
        "ged",
        "icv",
        "multispectral",
        "openNURBS",
        "optical",
        "orle",
        "p2t",
        "pc",
        "pkg",
        "render",
        "stepcore",
        "stepdai",
        "stepeditor",
        "steputils",
        "termio",
        "termlib",
        "utahrle",
        "vds",
    ]))

    brlcad_library_names = [
    #"bu", "bn", "db5", "nmg", "pc", "rtgeom", "brep", "raytrace", "wdb", "brep",
    "bu", "bn", "brep", "wdb",
    "rt",
    ] # wow, this extra character caused lots of problems: ,

    brlcad_libraries = {}

    # Make the plan of action for generating all the bindings and wrappers.
    for brlcad_library_name in brlcad_library_names:
        brlcad_library_header_name = brlcad_library_name

        # TODO: figure out a better way to support this silly edge case. The
        # library "librt.so" is exporting symbols defined in "raytrace.h" which
        # isn't something I originally expected when writing this function.
        if brlcad_library_name == "rt":
            brlcad_library_header_name = "raytrace"

        if is_win32():
            # BRLCAD users might install 64-bit BRLCAD to "Program Files
            # (x86)". This will need to be fixed in the future. Basically, if
            # the dll files can be imported through ctypes, then that dll file
            # can be used, and if not, then default to trying to find 32-bit
            # BRLCAD dlls.
            if is_py32():
                arch = " (x86)"
            else:
                arch = ""

            # if 64-bit BRLCAD doesn't exist then assume 32-bit BRLCAD (64-bit
            # BRLCAD might be installed there)
            if len(glob.glob("C:\\Program Files\\BRLCAD*\\*")) == 0:
                arch = " (x86)"

            # TODO: ctypesgen will generate libbu.py but the path to the dll
            # file (in the .py file) will be "C:\whatever\etc" which is
            # problematic because of escape characters. Consequently, the dll
            # wont be able to be loaded in this situation. The temporary
            # solution is to assume that brlcad has been installed
            # "system-wide" and that the DLL files will be discoverable just by
            # filename. This problem doesn't happen with the header files
            # because the header file paths are never inserted into the final
            # .py file (the header file paths are just consumed by ctypesgen
            # itself).
            shared_library = "lib{1}.dll".format(arch, brlcad_library_name)
            #shared_library = "C:\\Program Files{0}\\BRLCAD*\\bin\\lib{1}.dll".format(arch, brlcad_library_name)
            #shared_library = glob.glob(shared_library)[0]
            # TODO: the above problem might be solvable by checking the output
            # of that last glob() call. Maybe replace "\" with "\\" and that
            # will fix the ctypesgen problem? This is a problematic solution
            # because what if "\" is genuinely in the name of a Windos file?

            header = "C:\\Program Files{0}\\BRLCAD*\\include\\brlcad\\{1}.h".format(arch, brlcad_library_header_name)
            header = glob.glob(header)[0]
        else:
            # hardcoding these paths for now
            shared_library = "/usr/brlcad/lib/lib{0}.so".format(brlcad_library_name)
            header = "/usr/brlcad/include/brlcad/{0}.h".format(brlcad_library_header_name)

        brlcad_library = {
            "name": brlcad_library_name,
            "library_name": "lib{0}".format(brlcad_library_name),
            "shared_library": shared_library,
            "header": header,
            "dependencies": [],
        }

        logger.debug("brlcad_library_name is: {0}".format(str(brlcad_library_name)))
        logger.debug("brlcad_library_name type: {0}".format(str(type(brlcad_library_name))))
        brlcad_libraries[brlcad_library_name] = brlcad_library

    def setup_dependencies(brlcad_libraries):
        """
        Make up the dependencies to each library so that ctypesgen will be able
        to import the relevant structures from each module.
        """
        brlcad_libraries["wdb"]["dependencies"] += ["bu", "bn"]
        #brlcad_libraries["rtgeom"]["dependencies"] += ["bu", "brep"]
        #brlcad_libraries["raytrace"]["dependencies"] += ["bu", "bn", "db5", "nmg", "pc", "rtgeom"]

        # not sure about the capitalization on this one
        #brlcad_libraries["brep"]["dependencies"].append("openNURBS")

        return brlcad_libraries

    def setup_dependency_modules(brlcad_libraries):
        """
        This converts from library names to the absolute module import name so
        that ctypesgen can access previous modules instead of re-creating the
        same symbols multiple times.
        """
        for brlcad_library in brlcad_libraries.values():
            modules = []
            for module_name in set(brlcad_library["dependencies"]):
                #dependency_module = "brlcad._bindings.lib{0}".format(module_name)
                dependency_module = "lib{0}".format(module_name)
                modules.append(dependency_module)
            brlcad_library["dependency_modules"] = modules
        return brlcad_libraries

    brlcad_libraries = setup_dependencies(brlcad_libraries)
    #brlcad_libraries = setup_dependency_modules(brlcad_libraries)

    # this is where the generated files are placed
    bindings_path = os.path.join(library_path, "_bindings")
    logger.debug("bindings_path is {0}".format(bindings_path))

    cleanup_bindings_dir(bindings_path, logger=logger)

    # Holds the name of a module and the names that the module defines.
    symbol_map = {}

    # List of libraries that have been generated by the following for loop.
    generated_libraries = []

    for name in brlcad_library_names:
        brlcad_library = brlcad_libraries[name]

        logger.debug("Processing library: {0}".format(brlcad_library))

        library_name = brlcad_library["library_name"]
        shared_library = brlcad_library["shared_library"]
        header_path = brlcad_library["header"]
        modules = brlcad_library["dependencies"]

        # location and name of the python file for this wrapper
        output_file_path = os.path.join(bindings_path, "{0}.py".format(library_name))

        # HACK: This is how ctypesgen is told to not re-define the same types.
        # The basic concept is to look through dependency_modules and see which
        # modules have already been generated (all of them should be generated
        # by now unless there's a dependency loop in BRL-CAD libraries...). The
        # symbols from each of the generated modules are passed in as
        # other_known_names so that ctypesgen doesn't redefine the
        # previously-generated names. The list of module names is passed in as
        # "modules" so that ctypesgen generates a python file that actually
        # imports those symbols.

        # Construct the list of types and other variables that are already
        # defined by other ctypesgen-generated files.
        other_known_names = []
        for module in modules:
            other_known_names.extend(symbol_map["lib" + module])

        # TODO: the ctypesgen printer might need to re-arrange when it imports
        # modules. It should probably happen before the preamble is printed, so
        # that the preamble is just cached instead of always redefining
        # everything. I think now that the preamble is an import line, the
        # types are already cached, so it's probably okay for the moment.

        # generate the wrapper bindings (woot)
        generate_wrapper(library_name, shared_library, header_path, output_file_path, modules=["lib{0}".format(nm) for nm in modules], other_known_names=other_known_names, logger=logger)
        generated_libraries.append(library_name)
        logger.debug("Done generating the wrapper file for {0}".format(library_name))

        # HACK: Load this latest generated library. Create the appropriate
        # __init__.py file and then import the current module. Add module ->
        # dir(module) to the list of known names. On the next pass, if
        # brlcad_library["dependency_modules"] has any values, then include the
        # list of known names from the data structure as "other_known_names".

        # 1) generate the appropriate __init__.py file (__all__ will need to be constructed)
        logger.debug("About to write the __init__.py file")
        generate_init_file(bindings_path, generated_libraries, lib_prefix_already_prepended=True, logger=logger)
        logger.debug("Okay, __init__.py has been updated.")

        # 2) load the latest generated module
        logger.debug("Loading the __init__.py module from {0}".format(bindings_path))
        init_module = imp.load_source("_bindings", os.path.join(bindings_path, "__init__.py"))

        module_path = os.path.join(bindings_path, "{0}.py".format(library_name))
        logger.debug("Loading the {0} module from {1}.".format(library_name, module_path))
        latest_module = imp.load_source(library_name, module_path)
        symbols = dir(latest_module)

        # 3) store the list of defined names from that module by running dir(loaded_module)
        symbol_map[library_name] = symbols

        # TODO: confirm the following TODO statement. It looks like this should
        # be working now?
        # TODO: ctypesgen needs to support "other_known_names" being passed in
        # through options (right now it just overrides this value).

def generate_init_file(bindings_path, generated_library_names, lib_prefix_already_prepended=False, logger=None):
    """
    Generates the __init__.py file based on the current list of generated
    wrappers.
    """
    # absolute path to where the __init__.py file should be placed
    init_path = os.path.join(bindings_path, "__init__.py")
    logger.debug("Writing __init__.py to: {0}".format(init_path))

    library_names = []
    if not lib_prefix_already_prepended:
        library_names = ["lib{0}".format(x) for x in generated_library_names]
    else:
        library_names = generated_library_names

    # build the __init__.py file contents
    init_contents = "__all__ = " + json.dumps(library_names)

    # save the init file
    init_file = open(init_path, "w")
    init_file.write(init_contents)
    init_file.close()

    return True
