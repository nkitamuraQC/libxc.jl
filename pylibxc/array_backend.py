"""
Backend-agnostic array interface
"""

import ctypes
import sys
from . import dlpack


def _is_c_contiguous(shape, strides, itemsize):
    if strides is None:
        return True

    expected = itemsize
    for size, stride in zip(reversed(shape), reversed(strides)):
        if size > 1:
            if stride != expected:
                return False
            expected *= size
    return True


def _is_f_contiguous(shape, strides, itemsize):
    if strides is None:
        return True

    expected = itemsize
    for size, stride in zip(shape, strides):
        if size > 1:
            if stride != expected:
                return False
            expected *= size
    return True


class ArrayInterfacePointer(ctypes.c_void_p):
    @classmethod
    def from_param(cls, obj):
        if isinstance(obj, ctypes.c_void_p):
            return obj

        if (obj is None) and cls._nullable_:
            return cls(obj)

        if hasattr(obj, "__cuda_array_interface__"):
            array_interface = obj.__cuda_array_interface__
        elif hasattr(obj, "__array_interface__"):
            array_interface = obj.__array_interface__
        elif hasattr(obj, "__dlpack__"):
            dltensor = dlpack.from_capsule(obj.__dlpack__())
            array_interface = dltensor.__array_interface__
        else:
            raise TypeError(f"Unsupported type {type(obj)}")

        version = array_interface["version"]
        if version < 2:
            raise TypeError(
                f"__array_interface__ version is {version}, but must be >= 2"
            )

        ptr, readonly = array_interface["data"]
        if not ptr:
            raise TypeError(f"Invalid pointer: '{ptr}'")
        if not readonly <= cls._readonly_:
            raise TypeError("Array must be writable")

        shape = array_interface["shape"]
        if cls._ndim_ is not None and len(shape) != cls._ndim_:
            raise TypeError(
                f"Dimension mismatch, expected {cls._ndim_} but got {len(shape)}"
            )
        if cls._shape_ is not None and any(shape != cls._shape_):
            raise TypeError(f"Shape mismatch, expected {cls._shape_} but got {shape}")

        typestr = array_interface["typestr"]
        dtype = typestr[0], typestr[1], int(typestr[2:])
        if not cls._dtype_[0] == "|" and dtype[0] != cls._dtype_[0]:
            raise TypeError(
                f"Byteorder mismatch, expected {cls._dtype_[0]} but got {dtype[0]}"
            )
        if dtype[1] != cls._dtype_[1]:
            raise TypeError(
                f"Typecode mismatch, expected {cls._dtype_[1]} but got {dtype[1]}"
            )
        if dtype[2] != cls._dtype_[2]:
            raise TypeError(
                f"Itemsize mismatch, expected {cls._dtype_[2]} but got {dtype[2]}"
            )

        strides = array_interface.get("strides", None)
        if cls._contiguous_ and strides is not None:
            if any(s < 0 for s in strides):
                raise TypeError("Negative strides are not supported")
            if not (
                _is_c_contiguous(shape, strides, dtype[2])
                or _is_f_contiguous(shape, strides, dtype[2])
            ):
                raise TypeError("Array must be contiguous in memory")

        mask = array_interface.get("mask", None)
        if mask is not None:
            raise TypeError(f"Masked arrays are not supported")

        p = cls(ptr)
        p._keepalive = obj
        return p


_pointer_type_cache = {}


def pointer(typestr=None, ndim=None, shape=None, flags=None):
    cache_key = (typestr, ndim, shape, flags)
    if cache_key in _pointer_type_cache:
        return _pointer_type_cache[cache_key]

    readonly = True
    contiguous = False
    nullable = False
    if flags is not None:
        readonly = "W" not in flags
        contiguous = "C" in flags
        nullable = "N" in flags

    dtype = (typestr[0], typestr[1], int(typestr[2:]))
    if dtype[0] not in ["<", ">", "|"]:
        raise TypeError(
            f"Invalid byteorder {dtype[0]} (<: little-endian, >: big-endian, |: not-relevant)"
        )
    if dtype[1] not in ["b", "i", "u", "f", "c", "V"]:
        raise TypeError(
            f"Invalid typecode {dtype[1]} (b: bool, i: int, u: unsigned, f: float, c: complex, V: other)"
        )
    if dtype[2] <= 0:
        raise TypeError(f"Invalid itemsize {dtype[2]} (number of bytes the type uses)")
    name = "_".join([str(key) for key in cache_key if key is not None])
    cls = type(
        "ArrayInterfacePointer_" + name,
        (ArrayInterfacePointer,),
        {
            "_readonly_": readonly,
            "_dtype_": dtype,
            "_ndim_": ndim,
            "_shape_": shape,
            "_contiguous_": contiguous,
            "_nullable_": nullable,
        },
    )
    _pointer_type_cache[cache_key] = cls
    return cls


def is_convertible(x, T):
    if isinstance(x, T):
        return True
    try:
        T(x)
        return True
    except:
        return False


def _issubclass_fast(cls, modname, clsname):
    try:
        mod = sys.modules[modname]
    except KeyError:
        return False
    parent_cls = getattr(mod, clsname)
    return issubclass(cls, parent_cls)


def array_namespace(x):
    if hasattr(x, "__array_namespace__"):
        return x.__array_namespace__()

    cls = type(x)

    if _issubclass_fast(cls, "numpy", "ndarray") or _issubclass_fast(
        cls, "numpy", "generic"
    ):
        return sys.modules["numpy"]

    if _issubclass_fast(cls, "cupy", "ndarray"):
        return sys.modules["cupy"]

    if _issubclass_fast(cls, "torch", "Tensor"):
        return sys.modules["torch"]

    if _issubclass_fast(cls, "jax", "Array"):
        return sys.modules["jax"]

    raise TypeError(f"{cls.__name__} is not a supported array type")
