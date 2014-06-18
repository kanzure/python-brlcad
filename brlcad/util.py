"""
Various functions which can be used in all other modules.
"""

from distutils.version import StrictVersion
from brlcad._bindings import BRLCAD_VERSION


def check_missing_params(method_name, **kwargs):
    missing_params = []
    for param, value in enumerate(kwargs):
        if value is None:
            missing_params.append(param)
    if missing_params:
        raise ValueError("Missing parameters while calling {}: {}".format(method_name, missing_params))


def compare_version(version):
    """
    Returns 1 if the given version is bigger than the wrapped BRL-CAD, -1 if it is smaller, 0 if it is equal.
    """
    if not isinstance(version, StrictVersion):
        version = StrictVersion(version)

    # returns 1 if the given version is bigger than the wrapped BRL-CAD version
    if version > BRLCAD_VERSION:
        return 1

    # returns -1 if the given version is smaller than the wrapped BRL-CAD version
    elif version < BRLCAD_VERSION:
        return -1

    # returns 0 if the versions are equal
    else:
        return 0
