"""
https://dmlc.github.io/dlpack/latest/python_spec.html
https://github.com/numpy/numpy/blob/main/numpy/_core/src/common/dlpack/dlpack.h
"""

import ctypes
import weakref


ctypes.pythonapi.PyCapsule_IsValid.argtypes = [ctypes.py_object, ctypes.c_char_p]
ctypes.pythonapi.PyCapsule_IsValid.restype = ctypes.c_int

ctypes.pythonapi.PyCapsule_GetPointer.argtypes = [ctypes.py_object, ctypes.c_char_p]
ctypes.pythonapi.PyCapsule_GetPointer.restype = ctypes.c_void_p

ctypes.pythonapi.PyCapsule_SetName.argtypes = [ctypes.py_object, ctypes.c_char_p]
ctypes.pythonapi.PyCapsule_SetName.restype = ctypes.c_int


CAPSULE_NAME = b"dltensor"
CAPSULE_NAME_VER = b"dltensor_versioned"
CAPSULE_USED = b"used_dltensor"
CAPSULE_USED_VER = b"used_dltensor_versioned"


class DLPackVersion(ctypes.Structure):
    _fields_ = [
        ("major", ctypes.c_uint32),
        ("minor", ctypes.c_uint32),
    ]


class DLDeviceType(ctypes.c_int32):
    kDLCPU = 1
    kDLCUDA = 2
    kDLCUDAHost = 3
    kDLOpenCL = 4
    kDLVulkan = 7
    kDLMetal = 8
    kDLVPI = 9
    kDLROCM = 10
    kDLROCMHost = 11
    kDLExtDev = 12
    kDLCUDAManaged = 13
    kDLOneAPI = 14
    kDLWebGPU = 15
    kDLHexagon = 16
    kDLMAIA = 17


class DLDevice(ctypes.Structure):
    _fields_ = [
        ("device_type", DLDeviceType),
        ("device_id", ctypes.c_int32),
    ]


class DLDataTypeCode(ctypes.c_uint8):
    kDLInt = 0
    kDLUInt = 1
    kDLFloat = 2
    kDLOpaqueHandle = 3
    kDLBfloat = 4
    kDLComplex = 5
    kDLBool = 6

    def __str__(self):
        return {
            self.kDLInt: "i",
            self.kDLUInt: "u",
            self.kDLFloat: "f",
            self.kDLOpaqueHandle: "V",
            # self.kDLBfloat
            self.kDLComplex: "c",
            self.kDLBool: "b",
        }[self.value]


class DLDataType(ctypes.Structure):
    _fields_ = [
        ("code", DLDataTypeCode),
        ("bits", ctypes.c_uint8),
        ("lanes", ctypes.c_uint16),
    ]


class DLTensor(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.c_void_p),
        ("device", DLDevice),
        ("ndim", ctypes.c_int32),
        ("dtype", DLDataType),
        ("shape", ctypes.POINTER(ctypes.c_int64)),
        ("strides", ctypes.POINTER(ctypes.c_int64)),
        ("byte_offset", ctypes.c_uint64),
    ]

    @property
    def itemsize(self):
        return self.dtype.lanes * self.dtype.bits // 8

    @property
    def __array_interface__(self):
        shape = tuple(self.shape[dim] for dim in range(self.ndim))
        if self.strides:
            strides = tuple(
                self.strides[dim] * self.itemsize for dim in range(self.ndim)
            )
        else:
            strides = None
        typestr = "|" + str(self.dtype.code)[0] + str(self.itemsize)
        data = int(self.data) + int(self.byte_offset)
        array_interface = dict(
            version=3,
            shape=shape,
            strides=strides,
            data=(data, False),
            typestr=typestr,
        )
        return array_interface


class DLManagedTensor(ctypes.Structure):
    _fields_ = [
        ("dl_tensor", DLTensor),
        ("manager_ctx", ctypes.c_void_p),
        (
            "deleter",
            ctypes.CFUNCTYPE(
                None,
                ctypes.c_void_p,  # ctypes.POINTER(DLManagedTensor)
            ),
        ),
    ]

    @property
    def __array_interface__(self):
        return self.dl_tensor.__array_interface__


class DLManagedTensorVersioned(ctypes.Structure):
    _fields_ = [
        ("version", DLPackVersion),
        ("manager_ctx", ctypes.c_void_p),
        (
            "deleter",
            ctypes.CFUNCTYPE(
                None,
                ctypes.c_void_p,  # ctypes.POINTER(DLManagedTensorVersioned)
            ),
        ),
        ("flags", ctypes.c_uint64),
        ("dl_tensor", DLTensor),
    ]

    @property
    def __array_interface__(self):
        return self.dl_tensor.__array_interface__


def _install_deleter(obj, ptr):
    def _finalizer(p=ptr):
        if p and p.contents.deleter:
            p.contents.deleter(p)

    weakref.finalize(obj, _finalizer)


def from_capsule(obj):
    # Convert to PyObject
    capsule = ctypes.py_object(obj)

    # Extract pointer to tensor object from capsule
    if ctypes.pythonapi.PyCapsule_IsValid(capsule, CAPSULE_NAME) != 0:
        managed = ctypes.cast(
            ctypes.pythonapi.PyCapsule_GetPointer(capsule, CAPSULE_NAME),
            ctypes.POINTER(DLManagedTensor),
        )
        used_name = CAPSULE_USED
    elif ctypes.pythonapi.PyCapsule_IsValid(capsule, CAPSULE_NAME_VER) != 0:
        managed = ctypes.cast(
            ctypes.pythonapi.PyCapsule_GetPointer(capsule, CAPSULE_NAME_VER),
            ctypes.POINTER(DLManagedTensorVersioned),
        )
        used_name = CAPSULE_USED_VER
    else:
        raise RuntimeError("Invalid DLPack capsule")

    # Check that there is actually something in the capsule
    if not managed:
        raise RuntimeError("Could not extract tensor from DLPack capsule")

    # Rename capsule to signal consumption
    if ctypes.pythonapi.PyCapsule_SetName(capsule, used_name) != 0:
        raise RuntimeError("Failed to mark DLPack capsule as used")

    dltensor = managed.contents

    # Keep capsule alive so producer destructor doesn't run early
    dltensor._capsule = obj

    # Install finalizer to call DLPack deleter
    _install_deleter(dltensor, managed)

    return dltensor
