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
    if BRLCAD_VERSION < version:
        return 1
    elif BRLCAD_VERSION > version:
        return -1
    else:
        return 0
