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

import os
import json
import logging
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

def generate_wrapper(libname, libpath, header_path, outputfile, logger, debug=False):
    """
    Generate a ctypes wrapper around the library.

    @param libname: library name
    @param libpath: path to the shared library
    @param header_path: single header file to scan for symbols
    @param outputfile: location at which to dump python source code
    @param debug: toggle additional ctypesgen error/warning output
    """
    options = lambda: 0;

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
    options.modules = []
    options.include_search_paths = [] # TODO
    options.compile_libdirs = []
    options.runtime_libdirs = []

    options.header_template = None
    options.strip_build_path = None
    options.inserted_files = []

    options.other_known_names = set()

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

def main(library_path, logger=None):
    if not logger:
        logger = setup_logging()

    logger.debug("ctypesgencore version is {0}".format(ctypesgencore.__version__))

    # Temporary variable for storing a list of library files that are
    # generated. This is then used to assemble the __init__.py file.
    library_names = []

    # plan of action for generating all the bindings and wrappers
    brlcad_libraries = [
        {
            "name": "bu",
            "library_name": "libbu",
            "shared_library": "/usr/brlcad/lib/libbu.so",
            "header": "/home/kanzure/local/brlcad/brlcad/include/bu.h",
        },
    ]

    # this is where the generated files are placed
    bindings_path = os.path.join(library_path, "_bindings/")
    logger.debug("bindings_path is {0}".format(bindings_path))

    try:
        # make the _bindings folder
        os.makedirs(bindings_path)
    except OSError as error:
        # _bindings already exists, should be okay
        logger.debug("_bindings path already exists, should be okay")

    for brlcad_library in brlcad_libraries:
        logger.debug("Processing library: {0}".format(brlcad_library))

        library_name = brlcad_library["library_name"]
        shared_library = brlcad_library["shared_library"]
        header_path = brlcad_library["header"]

        # location and name of the python file for this wrapper
        output_file_path = os.path.join(bindings_path, "{0}.py".format(library_name))

        # generate the wrapper bindings (woot)
        generate_wrapper(library_name, shared_library, header_path, output_file_path, logger=logger)

        # include it in __init__.py later
        library_names.append(library_name)

    # absolute path to where the __init__.py file should be placed
    init_path = os.path.join(bindings_path, "__init__.py")
    logger.debug("Writing __init__.py to: {0}".format(init_path))

    # build the __init__.py file contents
    init_contents = "__all__ = " + json.dumps(library_names)

    # save the init file
    init_file = open(init_path, "w")
    init_file.write(init_contents)
    init_file.close()
