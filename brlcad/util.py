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


def min_brlcad_version(version):
    """
    Returns True if the wrapped BRL-CAD version is >= than the given version.
    """
    return BRLCAD_VERSION >= StrictVersion(version)
