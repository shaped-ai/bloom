import os
import glob
import pkg_resources
import cffi


def _find_libbloomf_dll_paths():
    """
    Finds the libbloomf dynamic library file.
    """
    here = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))

    def make_paths(ext):
        return [
            *glob.glob(os.path.join(here, "libbloomf*.{}".format(ext))),
            *glob.glob(os.path.join(here, "..", "libbloomf*.{}".format(ext))),
            *glob.glob(os.path.join(here, "../..", "libbloomf*.{}".format(ext))),
        ]

    return make_paths("so") + make_paths("dll") + make_paths("pyd")


def _get_libbloomf_header_file():
    """
    Retrieve the preamble header file necessary for the bloom dynamic library.
    """
    pkg_name = __name__.split(".")[0]
    return pkg_resources.resource_filename(pkg_name, "golib/cdef.h")


def load_bloom_filter_dll():
    """
    Loads and returns an ffi context and the bloom filter dynamic library file.
    """
    ffi = cffi.FFI()

    dll_paths = _find_libbloomf_dll_paths()
    if not dll_paths:
        raise RuntimeError("Can't find any libbloomf dynamic library files")

    with open(_get_libbloomf_header_file(), "r") as f:
        file_data = f.read()
        ffi.cdef(file_data)

    lib = ffi.dlopen(dll_paths[0])
    return ffi, lib
