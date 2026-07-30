"""Detect prebuilt ninTexUtils Cython modules without compiling at import time.

The old ``pyximport`` probe could invoke a compiler during a normal Blender
import and then fail noisily on a machine without a matching toolchain.  The
vendored Cython sources remain usable by a package build, but runtime addon
imports only accept already-built extension modules.
"""

try:
    from . import cython_available  # noqa: F401
except Exception:
    is_available = False
else:
    is_available = True
