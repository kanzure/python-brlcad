
from brlcad.install.post_install import *
from brlcad.install.options import *
logger = setup_logging()
config = load_config()

# try this with and without brl-cad on the PATH:
print "find_brlcad_installations:\n", find_brlcad_installations(config, logger)

version_list = load_brlcad_options(config)

print "Version list:"
for version in version_list:
    print version

gcc_info = check_gcc(config, logger)
print "\nGCC info:\n", gcc_info

print "load_ctypesgen_options:\n", load_ctypesgen_options("/some/bindings/path", logger)


