"""
brlcad._ctypes_wrapper.bu
~~~~~~~~~~~~~~~~

Low-level ctypes wrapper around libbu.
"""

import ctypes

import _libloader
_libbu = _libloader.load("libbu")

from _headers import (
    time_t,
    off_t,
)

_libbu.bu_version.restype = ctypes.c_char_p
bu_version = _libbu.bu_version

def parse_version_data(func):
    """
    Calls a function to get version data and parses that version data into a
    dictionary.
    """
    data = func()

    # find the version number
    version = [x for x in data.split("\n")[0].split(" ") if len(x) > 0 and x[0].isdigit()][0]

    # a short string of text
    description = data.split("\n")[0].split("  ")[1]

    output = {
        "version": version,
        "description": description,
    }

    return output

__version_data__ = parse_version_data(_libbu.bu_version)
__version__ = __version_data__["version"]
__description__ = __version_data__["description"]

# brlcad/include/bu.h: 768
BU_LITTLE_ENDIAN = 1234
BU_BIG_ENDIAN = 4321
BU_PDP_ENDIAN = 3412

bu_endian_t = ctypes.c_int

_libbu.bu_byteorder.argtypes = []
_libbu.bu_byteorder.restype = bu_endian_t
bu_byteorder = _libbu.bu_byteorder

class struct_bu_list(ctypes.Structure):
    pass
