import importlib
import os

XC_TEST_FLAGS = os.environ.get("XC_TEST_FLAGS", "XC_FLAGS_ON_HOST")
if XC_TEST_FLAGS == "XC_FLAGS_ON_HOST":
    XC_TEST_BACKEND = os.environ.get("XC_TEST_BACKEND", "numpy")
    ns = importlib.import_module(XC_TEST_BACKEND)
elif XC_TEST_FLAGS == "XC_FLAGS_ON_DEVICE":
    XC_TEST_BACKEND = os.environ.get("XC_TEST_BACKEND", "cupy")
    ns = importlib.import_module(XC_TEST_BACKEND)
else:
    raise Exception(f"Environment variable XC_TEST_FLAGS has unsupported value: '{XC_TEST_FLAGS}'")

if XC_TEST_BACKEND == "jax.numpy":
    from .functional import _ndptr_w
    _ndptr_w._readonly_ = True # Pretend that JAX arrays are mutable

XC_TEST_VERBOSE = os.environ.get("XC_TEST_VERBOSE")
if XC_TEST_VERBOSE:
    print(f"XC_TEST_FLAGS = {XC_TEST_FLAGS}")
    print(f"XC_TEST_BACKEND = {XC_TEST_BACKEND}")

def asarray(*args, **kwargs):
    return ns.asarray(*args, **kwargs)

def allclose(*args, **kwargs):
    return ns.allclose(*args, **kwargs)
