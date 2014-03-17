import types
import brlcad._bindings.libged as libged

header_file = "/home/csaba/dev/brlcad/trunk/include/ged.h"
implemented = {"ged_ls", "ged_open", "ged_init", "ged_close", "ged_3ptarb", "ged_in"}

ged_names = [x for x in dir(libged) if x.startswith('ged_') and not issubclass(type(getattr(libged, x)), types.TypeType)]

print "Number of entries: ", len(ged_names)

gedh = open(header_file).read()

import re

header_pattern = re.compile("GED_EXPORT extern [^(]*(ged_\w+)\(([^;]*)\);")
ws_pattern = re.compile("\s+")

args_map = {}
for match in header_pattern.finditer(gedh):
    cmd_name = match.group(1)
    if cmd_name not in ged_names:
        print "Command not found: {}".format(cmd_name)
    args_map[cmd_name] = ws_pattern.sub(' ', match.group(2))

for name in ged_names:
    if name not in args_map:
        print "Arguments not found: {}".format(name)

print "#*********** TODO: implement explicit list of params *******************#"

for name in ged_names:
    if name in implemented:
        continue
    cmd_args = args_map.get(name, "Args missing !")
    if cmd_args != "struct ged *gedp, int argc, const char *argv[]":
        continue
    cmd_name = name.replace('ged_', '')
    method_name = cmd_name
    if method_name in globals() or method_name in dir(__builtins__):
        method_name = 'ged_' + name
    print '    @ged_command\n' \
          '    def {}(self, *args):\n' \
          '        return self.execute_command(libged.{}, *args)\n'.format(
        method_name, name, cmd_name
    )

print "#********************* TODO: wrap params ******************************#"

for name in ged_names:
    if name in implemented:
        continue
    cmd_args = args_map.get(name, "Args missing !")
    if cmd_args == "struct ged *gedp, int argc, const char *argv[]":
        continue
    cmd_name = name.replace('ged_', '')
    method_name = cmd_name
    if method_name in globals() or method_name in dir(__builtins__):
        method_name = 'ged_' + name
    print '    @ged_command\n' \
          '    def {}(self, *args):\n' \
          '        # todo: wrap params: {}\n' \
          '        # return self.execute_command(libged.{}, "{}", *args)\n' \
          '        raise NotImplementedError("Not implemented yet !")\n'.format(
        method_name, cmd_args, name, cmd_name
    )
