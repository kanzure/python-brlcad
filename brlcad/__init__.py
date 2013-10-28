import os as _os

__all__ = []

_path_bindings = _os.path.join(_os.path.dirname(__file__), "_bindings")

# The generated bindings might not exist yet and importing will fail.
if _os.path.exists(_path_bindings):
    __all__.append("_bindings")
