"""
Find the LibXC shared object and imports it as core.
"""

import ctypes
import ctypes.util
import os
import sys
import sysconfig

# Attempt to load the compiled C code
core = None
__libxc_path = None


def _load_library(libname, loader_path):
    """Lifted from numpy.ctypeslib"""
    libname = os.fsdecode(libname)
    loader_path = os.fsdecode(loader_path)
    ext = os.path.splitext(libname)[1]
    if not ext:
        import sys
        import sysconfig
        base_ext = ".so"
        if sys.platform.startswith("darwin"):
            base_ext = ".dylib"
        elif sys.platform.startswith("win"):
            base_ext = ".dll"
        libname_ext = [libname + base_ext]
        so_ext = sysconfig.get_config_var("EXT_SUFFIX")
        if not so_ext == base_ext:
            libname_ext.insert(0, libname + so_ext)
    else:
        libname_ext = [libname]

    loader_path = os.path.abspath(loader_path)
    if not os.path.isdir(loader_path):
        libdir = os.path.dirname(loader_path)
    else:
        libdir = loader_path

    for ln in libname_ext:
        libpath = os.path.join(libdir, ln)
        if os.path.exists(libpath):
            try:
                return ctypes.cdll[libpath]
            except OSError:
                # defective lib file
                raise
    raise OSError("no file with expected extension")


def _preferred_libxc_candidates():
    """Return likely LibXC library paths in priority order."""
    candidates = []

    env_path = os.environ.get("LIBXC_PATH")
    if env_path:
        candidates.append(env_path)

    # Prefer Homebrew-installed LibXC on macOS, which is usually the proper ARM64 build.
    for base in [
        "/opt/homebrew/lib",
        "/usr/local/lib",
        "/usr/lib",
    ]:
        for name in ["libxc.dylib", "libxc.15.dylib", "libxc.so", "libxc.so.15"]:
            candidates.append(os.path.join(base, name))

    # Also consider the common Homebrew opt path.
    opt_path = "/opt/homebrew/opt/libxc/lib"
    if os.path.isdir(opt_path):
        for name in ["libxc.dylib", "libxc.15.dylib"]:
            candidates.append(os.path.join(opt_path, name))

    # Finally, fall back to the library search path used by the system.
    system_lib = ctypes.util.find_library("xc")
    if system_lib:
        candidates.append(system_lib)

    # Deduplicate while preserving order.
    seen = set()
    out = []
    for cand in candidates:
        if cand not in seen:
            seen.add(cand)
            out.append(cand)
    return out


# First check the local folder, then try a curated list of likely LibXC paths.
libxc_loaded = False
for candidate in [os.path.abspath(os.path.dirname(__file__))] + _preferred_libxc_candidates():
    try:
        if os.path.isdir(candidate):
            __libxc_path = os.path.abspath(candidate)
            core = _load_library("libxc", __libxc_path)
        else:
            __libxc_path = candidate
            core = ctypes.CDLL(candidate)
        libxc_loaded = True
        break
    except Exception:
        continue

if not libxc_loaded:
    raise ImportError(
        "LibXC Shared object not found, searched Python module local directory and library paths"
    )


def get_core_path():
    """
    Returns the path of the loaded LibXC shared object.
    """

    return __libxc_path
