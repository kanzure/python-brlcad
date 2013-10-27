import os

__all__ = []

_path_bindings = os.path.join(os.path.dirname(__file__), "_bindings")

# The generated bindings might not exist yet and importing will fail.
if os.path.exists(_path_bindings):
    __all__.append("_bindings")
