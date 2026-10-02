"""
Binds a LibXC Functional struct to a Python object
"""

import ctypes
import os

from .core import core
from . import array_backend
from . import flags
from . import util
from . import structs

### Bind required ctypes

_ndptr = array_backend.pointer(typestr="|f8", flags=("C",))
_ndptr_w = array_backend.pointer(typestr="|f8", flags=("W", "C", "N"))

_xc_func_p = ctypes.POINTER(structs.xc_func_type)
_xc_func_info_p = ctypes.POINTER(structs.xc_func_info_type)

# Bind only symbols that are actually available in the linked LibXC.
def _bind_if_present(name, argtypes=None, restype=None):
    if not hasattr(core, name):
        return None
    func = getattr(core, name)
    if argtypes is not None:
        func.argtypes = argtypes
    if restype is not None:
        func.restype = restype
    return func

# Allocation wrappers
_xc_func_alloc = _bind_if_present("xc_func_alloc", restype=_xc_func_p)
_xc_func_init = _bind_if_present("xc_func_init", argtypes=(_xc_func_p, ctypes.c_int, ctypes.c_int), restype=ctypes.c_int)
_xc_func_end = _bind_if_present("xc_func_end", argtypes=(_xc_func_p,))
_xc_func_free = _bind_if_present("xc_func_free", argtypes=(_xc_func_p,))

if _xc_func_alloc is None:
    raise AttributeError("LibXC shared library does not expose xc_func_alloc")
if _xc_func_init is None:
    raise AttributeError("LibXC shared library does not expose xc_func_init")

# Keep backward-compatible names for the rest of the file.
core.xc_func_alloc = _xc_func_alloc
core.xc_func_init = _xc_func_init
core.xc_func_end = _xc_func_end
core.xc_func_free = _xc_func_free

# Info wrappers
_bind_if_present("xc_func_get_info", argtypes=(_xc_func_p,), restype=_xc_func_info_p)
_bind_if_present("xc_func_info_get_kind", argtypes=(_xc_func_info_p,))
_bind_if_present("xc_func_info_get_name", argtypes=(_xc_func_info_p,), restype=ctypes.c_char_p)
_bind_if_present("xc_func_info_get_family", argtypes=(_xc_func_info_p,))
_bind_if_present("xc_func_info_get_flags", argtypes=(_xc_func_info_p,))
_bind_if_present("xc_func_info_get_references", argtypes=(_xc_func_info_p, ctypes.c_int), restype=ctypes.POINTER(structs.func_reference_type))
_bind_if_present("xc_func_info_get_n_ext_params", argtypes=(_xc_func_info_p,))
_bind_if_present("xc_func_info_get_ext_params_name", argtypes=(_xc_func_info_p, ctypes.c_int), restype=ctypes.c_char_p)
_bind_if_present("xc_func_info_get_ext_params_description", argtypes=(_xc_func_info_p, ctypes.c_int), restype=ctypes.c_char_p)
_bind_if_present("xc_func_info_get_ext_params_default_value", argtypes=(_xc_func_info_p, ctypes.c_int), restype=ctypes.c_double)
_bind_if_present("xc_func_info_get_number", argtypes=(_xc_func_info_p,), restype=ctypes.c_int)
_bind_if_present("xc_func_info_get_kind", argtypes=(_xc_func_info_p,))
_bind_if_present("xc_num_aux_funcs", argtypes=(_xc_func_p,), restype=ctypes.c_int)
_bind_if_present("xc_aux_func_ids", argtypes=(_xc_func_p, ctypes.POINTER(ctypes.c_int)))
_bind_if_present("xc_aux_func_weights", argtypes=(_xc_func_p, ctypes.POINTER(ctypes.c_double)))

# Setters
_bind_if_present("xc_func_set_ext_params", argtypes=(_xc_func_p, _ndptr))

# Setters for thresholds
_bind_if_present("xc_func_set_dens_threshold", argtypes=(_xc_func_p, ctypes.c_double))
_bind_if_present("xc_func_set_zeta_threshold", argtypes=(_xc_func_p, ctypes.c_double))
_bind_if_present("xc_func_set_sigma_threshold", argtypes=(_xc_func_p, ctypes.c_double))
_bind_if_present("xc_func_set_tau_threshold", argtypes=(_xc_func_p, ctypes.c_double))
_bind_if_present("xc_func_set_fhc_enforcement", argtypes=(_xc_func_p, ctypes.c_int))


# Bind computers
def _build_computer_argtype(num_nd, num_nd_write):
    """
    Small function to build the correct argtypes for the LibXC computers
    """
    ret = [_xc_func_p, ctypes.c_size_t]
    ret += [_ndptr] * num_nd
    ret += [_ndptr_w] * num_nd_write
    return tuple(ret)


# LDA computers
_bind_if_present("xc_lda", argtypes=_build_computer_argtype(1, 5))
_bind_if_present("xc_lda_exc_vxc", argtypes=_build_computer_argtype(1, 2))
_bind_if_present("xc_lda_exc", argtypes=_build_computer_argtype(1, 1))
_bind_if_present("xc_lda_vxc", argtypes=_build_computer_argtype(1, 1))
_bind_if_present("xc_lda_fxc", argtypes=_build_computer_argtype(1, 1))
_bind_if_present("xc_lda_kxc", argtypes=_build_computer_argtype(1, 1))
_bind_if_present("xc_lda_lxc", argtypes=_build_computer_argtype(1, 1))

# GGA computers
_bind_if_present("xc_gga", argtypes=_build_computer_argtype(2, 15))
_bind_if_present("xc_gga_exc_vxc", argtypes=_build_computer_argtype(2, 3))
_bind_if_present("xc_gga_exc", argtypes=_build_computer_argtype(2, 1))
_bind_if_present("xc_gga_vxc", argtypes=_build_computer_argtype(2, 2))
_bind_if_present("xc_gga_fxc", argtypes=_build_computer_argtype(2, 3))
_bind_if_present("xc_gga_kxc", argtypes=_build_computer_argtype(2, 4))
_bind_if_present("xc_gga_lxc", argtypes=_build_computer_argtype(2, 5))

# MGGA computers
_bind_if_present("xc_mgga", argtypes=_build_computer_argtype(4, 70))
_bind_if_present("xc_mgga_exc_vxc", argtypes=_build_computer_argtype(4, 5))
_bind_if_present("xc_mgga_exc", argtypes=_build_computer_argtype(4, 1))
_bind_if_present("xc_mgga_vxc", argtypes=_build_computer_argtype(4, 4))
_bind_if_present("xc_mgga_fxc", argtypes=_build_computer_argtype(4, 10))
_bind_if_present("xc_mgga_kxc", argtypes=_build_computer_argtype(4, 20))
_bind_if_present("xc_mgga_kxc", argtypes=_build_computer_argtype(4, 35))

# hybrid functions
_bind_if_present("xc_hyb_exx_coef", argtypes=(_xc_func_p,), restype=ctypes.c_double)
_bind_if_present("xc_hyb_cam_coef", argtypes=(_xc_func_p, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)))


### Build LibXCFunctional class

def _check_arrays(current_arrays, fields, sizes, factor, required, needs_lapl=False, needs_tau=False):
    """
    A specialized function built to construct and check the sizes of arrays given to the LibXCFunctional class.
    """

    # Nothing supplied so we build it out
    if current_arrays is None:
        current_arrays = {}

    for label in fields:
        # Determine if we need the output array
        label_required = required
        if (label.find('lapl') != -1) and not needs_lapl:
            label_required = False
        if (label.find('tau') != -1) and not needs_tau:
            label_required = False
        if label_required:
            size = sizes[label]
            current_arrays[label] = array_backend._zeros(shape=(factor, size))
        else:
            current_arrays[label] = None

    return current_arrays


class LibXCFunctional:
    def __init__(self, func_name, spin, func_flags = None):
        """
        The primary LibXCFunctional class used to build and compute DFT exchange-correlation quantities.

        Parameters
        ----------
        func_name : int or str
            Either the functional name or ID used to create the LibXCFunctional.
        spin : int or str
            The spin of the requested functional either "unpolarized" (1) or polarized" (2).
        func_flags : Optional[int]
            Flags to be passed to functional initialization, e.g. XC_FLAGS_ON_HOST or XC_FLAGS_ON_DEVICE.

        Returns
        -------
        func : LibXCFunctional
            A constructed LibXCFunctional.

        Examples
        --------
        # Build functional
        >>> func = pylibxc.LibXCFunctional("gga_c_pbe", "unpolarized")
        >>> print(func)
        <pylibxc.functional.LibXCFunctional (gga_c_pbe) object at 0x10544e048>

        >>> func.describe()
        Functional ID: 130
        Functional Name: gga_c_pbe
        Attributes:
            Name: Perdew, Burke & Ernzerhof
            Kind: 1
          Family: 2
        Citations:
           J. P. Perdew, K. Burke, and M. Ernzerhof, Phys. Rev. Lett. 77, 3865 (1996)
           J. P. Perdew, K. Burke, and M. Ernzerhof, Phys. Rev. Lett. 78, 1396 (1997)

        """
        self.xc_func = None
        self._xc_func_init = False

        # Handle func_name
        if isinstance(func_name, str):
            func_id = util.xc_functional_get_number(func_name)
            if func_id == -1:
                raise KeyError("LibXCFunctional: name '%s' not found." % func_name)
        elif array_backend.is_convertible(func_name, ctypes.c_int):
            func_id = func_name
            if util.xc_functional_get_name(func_name) is None:
                raise KeyError("LibXCFunctional: ID '%d' not found." % func_name)
        else:
            raise TypeError("LibXCFunctional: func_name must either be a string or int. Got {}".format(func_name))

        self._xc_func_name = util.xc_functional_get_name(func_id)

        # Handle spin
        if isinstance(spin, str):
            spin = spin.lower()
            if spin == "polarized":
                self._spin = 2
            elif spin == "unpolarized":
                self._spin = 1
            else:
                raise KeyError("LibXCFunctional: spin must either be 'polarized' or 'unpolarized' if represented by a string. Got {}".format(spin))
        else:
            self._spin = spin

        if self._spin not in [1, 2]:
            raise KeyError("LibXCFunctional: spin must either be 1 or 2 if represented by a integer. Got {}".format(self._spin))

        # Build the LibXC functional
        self.xc_func = core.xc_func_alloc()
        self.xc_func_size_names = [x for x in dir(self.xc_func.contents.dim) if "_" not in x]

        # Set all int attributes to zero (not all set to zero in libxc)
        for attr in self.xc_func_size_names:
            setattr(self.xc_func.contents, attr, 0)

        # Undocumented attribute to set obtain default for func_flags from environment, mainly for testing
        self._default_func_flags = vars(flags).get(os.environ.get("XC_TEST_FLAGS"))

        if func_flags is not None:
            if hasattr(core, "xc_func_init_flags"):
                ret = core.xc_func_init_flags(self.xc_func, func_id, self._spin, func_flags)
            else:
                raise ValueError(
                    "LibXC library does not expose xc_func_init_flags; please initialize without func_flags."
                )
        elif self._default_func_flags is not None:
            if hasattr(core, "xc_func_init_flags"):
                ret = core.xc_func_init_flags(self.xc_func, func_id, self._spin, self._default_func_flags)
            else:
                self._default_func_flags = None
                ret = core.xc_func_init(self.xc_func, func_id, self._spin)
        else:
            ret = core.xc_func_init(self.xc_func, func_id, self._spin)
        if ret != 0:
            raise ValueError("LibXC Functional construction did not complete. Error code %d" % ret)
        self._xc_func_init = True

        # Pull out all sizes after init
        self.xc_func_sizes = {}
        for attr in self.xc_func_size_names:
            self.xc_func_sizes[attr] = getattr(self.xc_func.contents.dim, attr)

        # Unpack functional info
        self.xc_func_info = core.xc_func_get_info(self.xc_func)
        self._number = core.xc_func_info_get_number(self.xc_func_info)
        self._kind = core.xc_func_info_get_kind(self.xc_func_info)
        self._name = core.xc_func_info_get_name(self.xc_func_info).decode("UTF-8")
        self._family = core.xc_func_info_get_family(self.xc_func_info)
        self._flags = core.xc_func_info_get_flags(self.xc_func_info)

        # Set needed flags
        self._needs_laplacian = (self._flags & flags.XC_FLAGS_NEEDS_LAPLACIAN) != 0
        self._needs_tau = (self._flags & flags.XC_FLAGS_NEEDS_TAU) != 0

        # Set derivatives
        self._have_exc = (self._flags & flags.XC_FLAGS_HAVE_EXC) != 0
        self._have_vxc = (self._flags & flags.XC_FLAGS_HAVE_VXC) != 0
        self._have_fxc = (self._flags & flags.XC_FLAGS_HAVE_FXC) != 0
        self._have_kxc = (self._flags & flags.XC_FLAGS_HAVE_KXC) != 0
        self._have_lxc = (self._flags & flags.XC_FLAGS_HAVE_LXC) != 0

        # Set omega
        self._have_cam = self._flags & flags.XC_FLAGS_HYB_CAM
        self._have_cam |= self._flags & flags.XC_FLAGS_HYB_CAMY
        self._have_cam |= self._flags & flags.XC_FLAGS_HYB_LC
        self._have_cam |= self._flags & flags.XC_FLAGS_HYB_LCY
        self._have_cam = self._have_cam != 0

        self._cam_omega = self._cam_alpha = self._cam_beta = False
        if self._have_cam:
            self._cam_omega = self.xc_func.contents.cam_omega
            self._cam_alpha = self.xc_func.contents.cam_alpha
            self._cam_beta = self.xc_func.contents.cam_beta

        elif self._family in [flags.XC_FAMILY_HYB_LDA, flags.XC_FAMILY_HYB_GGA, flags.XC_FAMILY_HYB_MGGA]:
            self._cam_alpha = self.xc_func.contents.cam_alpha

        # VV10
        self._have_vv10 = self._flags & flags.XC_FLAGS_VV10
        self._nlc_b = self._nlc_C = False
        if self._have_vv10:
            self._nlc_b = self.xc_func.contents.nlc_b
            self._nlc_C = self.xc_func.contents.nlc_C

        # Stable
        self._stable = self._flags & flags.XC_FLAGS_STABLE
        self._dev = self._flags & flags.XC_FLAGS_DEVELOPMENT

        # Pull out references
        self._refs = []
        self._bibtexs = []
        self._dois = []
        self._keys = []

        for pos in range(flags.XC_MAX_REFERENCES):
            ref = core.xc_func_info_get_references(self.xc_func_info, pos)
            if not ref:
                break

            self._refs.append(ref.contents.ref.decode("UTF-8"))
            self._bibtexs.append(ref.contents.bibtex.decode("UTF-8"))
            self._dois.append(ref.contents.doi.decode("UTF-8"))
            self._keys.append(ref.contents.key.decode("UTF-8"))

    def __del__(self):
        """
        Cleans up the LibXC C struct on deletion
        """
        if self.xc_func is None:
            return

        if self._xc_func_init:
            core.xc_func_end(self.xc_func)

        core.xc_func_free(self.xc_func)

    def __repr__(self):
        """
        Provides a simple string representation with functional name data.
        """
        return "<%s.%s (%s) object at %s>" % (self.__class__.__module__, self.__class__.__name__, self._xc_func_name,
                                              hex(id(self)))

    def describe(self):
        """
        Prints out a short description of the functional
        """

        ret = []
        ret.append("Functional ID: %s" % self._number)
        ret.append("Functional Name: %s" % self._xc_func_name)
        ret.append("Attributes:")
        ret.append("    Name: %s" % self._name)
        ret.append("    Kind: %d" % self._kind)
        ret.append("  Family: %d" % self._family)
        ret.append("Citations:")
        for x in self._refs:
            ret.append("   " + x)

        return "\n".join(ret)

    ### Getters

    def get_number(self):
        """
        Returns the LibXCFunctional ID.
        """

        return self._number

    def get_kind(self):
        """
        Returns the LibXCFunctional kind.
        """

        return self._kind

    def get_name(self):
        """
        Returns the LibXCFunctional name.
        """

        return self._name

    def get_family(self):
        """
        Returns the LibXCFunctional family.
        """

        return self._family

    def get_flags(self):
        """
        Returns the LibXCFunctional flags.
        """

        return self._flags

    def get_references(self):
        """
        Returns the LibXCFunctional references.
        """

        return self._refs

    def get_bibtex(self):
        """
        Returns the LibXCFunctional bibtex references.
        """

        return self._bibtexs

    def get_doi(self):
        """
        Returns the LibXCFunctional reference DOIs.
        """

        return self._dois

    def get_key(self):
        """
        Returns the LibXCFunctional reference keys.
        """

        return self._keys

    def get_hyb_exx_coef(self):
        """
        Returns the amount of global exchange to include.
        """

        if self._family not in [flags.XC_FAMILY_HYB_LDA, flags.XC_FAMILY_HYB_GGA, flags.XC_FAMILY_HYB_MGGA]:
            raise ValueError("get_hyb_exx_coef can only be called on hybrid functionals.")
        if self._have_cam:
            raise ValueError("get_hyb_exx_coef cannot be called on range-separated functionals.")

        return self._cam_alpha

    def get_cam_coef(self):
        """
        Returns the (omega, alpha, beta) quantities
        """

        if self._family not in [flags.XC_FAMILY_HYB_LDA, flags.XC_FAMILY_HYB_GGA, flags.XC_FAMILY_HYB_MGGA]:
            raise ValueError("get_cam_coef can only be called on hybrid functionals.")
        if not self._have_cam:
            raise ValueError("get_cam_coef can only be called on range-separated functionals.")

        return (self._cam_omega, self._cam_alpha, self._cam_beta)

    def get_vv10_coef(self):
        """
        Returns the VV10 (b, C) coefficients
        """

        if self._nlc_b is False:
            raise ValueError("get_vv10_coeff can only be called on -V functionals.")

        return (self._nlc_b, self._nlc_C)

    def aux_funcs(self, return_ids=False):
        """Gets any auxiliary functionals used by this functional.

        Returns None if the functional is not a mixed functional,
        otherwise an array of tuples of functional identifiers and
        weights.

        return_ids: return numerical IDs instead of names. False by
        default, so that names are returned.
        """

        naux = core.xc_num_aux_funcs(self.xc_func)
        if naux == 0:
            return None

        ids = (ctypes.c_int*naux)()
        core.xc_aux_func_ids(self.xc_func, ctypes.cast(ids, ctypes.POINTER(ctypes.c_int)))
        weights = (ctypes.c_double*naux)()
        core.xc_aux_func_weights(self.xc_func, ctypes.cast(weights, ctypes.POINTER(ctypes.c_double)))

        if return_ids:
            return list(zip(ids, weights))
        else:
            names = [util.xc_functional_get_name(id) for id in ids]
            return list(zip(names, weights))

    ### Setters

    def get_ext_param_names(self):
        """
        Gets the names of all external parameters
        """
        num_param = core.xc_func_info_get_n_ext_params(self.xc_func_info)

        ret = []
        for p in range(num_param):
            tmp = core.xc_func_info_get_ext_params_name(self.xc_func_info, p)
            ret.append(tmp.decode("UTF-8"))

        return ret

    def get_ext_param_descriptions(self):
        """
        Gets the descriptions of all external parameters
        """
        num_param = core.xc_func_info_get_n_ext_params(self.xc_func_info)

        ret = []
        for p in range(num_param):
            tmp = core.xc_func_info_get_ext_params_description(self.xc_func_info, p)
            ret.append(tmp.decode("UTF-8"))

        return ret

    def get_ext_param_default_values(self):
        """
        Gets the default values of all external parameters.
        """
        num_param = core.xc_func_info_get_n_ext_params(self.xc_func_info)

        ret = []
        for p in range(num_param):
            tmp = core.xc_func_info_get_ext_params_default_value(self.xc_func_info, p)
            ret.append(tmp)

        return ret

    def set_ext_params(self, ext_params):
        """
        Sets all external parameters.
        """
        num_param = core.xc_func_info_get_n_ext_params(self.xc_func_info)
        if num_param == 0:
            raise ValueError("LibXCFunctional '%s' has no external parameters to set." % self.get_name())

        if len(ext_params) != num_param:
            raise ValueError(
                "The length of the input external parameters (%d) does not match the length of the functional's external parameters (%d)."
                % (len(ext_params), num_param))

        _ext_params = (ctypes.c_double * num_param)(*ext_params)
        core.xc_func_set_ext_params(self.xc_func, ctypes.cast(_ext_params, ctypes.c_void_p))

    def set_dens_threshold(self, dens_threshold):
        """
        Sets the density threshold below which the functional will not be evaluated.
        """

        if dens_threshold < 0:
            raise ValueError("The density threshold cannot be smaller than 0.")

        core.xc_func_set_dens_threshold(self.xc_func, ctypes.c_double(dens_threshold))

    def set_zeta_threshold(self, zeta_threshold):
        """
        Sets the spin polarization threshold below which components will not be evaluated.
        """

        if zeta_threshold < 0:
            raise ValueError("The spin polarization threshold cannot be smaller than 0.")

        core.xc_func_set_zeta_threshold(self.xc_func, ctypes.c_double(zeta_threshold))

    def set_sigma_threshold(self, sigma_threshold):
        r"""Sets the smallest value allowed for sigma = \sqrt(\gamma). Smaller
        values than this get overwritten in the evaluation.

        """

        if sigma_threshold < 0:
            raise ValueError("The sigma threshold cannot be smaller than 0.")

        core.xc_func_set_sigma_threshold(self.xc_func, ctypes.c_double(sigma_threshold))

    def set_tau_threshold(self, tau_threshold):
        """Sets the smallest value allowed for tau. Smaller values than this
        get overwritten in the evaluation.

        """

        if tau_threshold < 0:
            raise ValueError("The tau threshold cannot be smaller than 0.")

        core.xc_func_set_tau_threshold(self.xc_func, ctypes.c_double(tau_threshold))

    def set_fhc_enforcement(self, enforce_fhc):
        """Enables or disables enforcement of the Fermi hole curvature

        """

        core.xc_func_set_fhc_enforcement(self.xc_func, ctypes.c_int(enforce_fhc))

    def compute(self, inp, output=None, do_exc=True, do_vxc=True, do_fxc=False, do_kxc=False, do_lxc=False):
        """
        Evaluates the functional and its derivatives on a grid.

        Parameters
        ----------
        inp : array_like or dict of array_like
            A input dictionary of NumPy array-like structures that provide the density on a grid and its derivaties. These are labled:
                rho - the density on a grid
                sigma - the contracted density gradients
                lapl - the laplacian of the density
                tau - the kinetic energy density

            Each family of functionals requires different derivatives:
                LDA: rho
                GGA: rho, sigma
                MGGA: rho, sigma, lapl (optional), tau

        output : dict of array_like (optional, None)
            Contains a dictionary of NumPy array-like structures to use as output data. If none are supplied this
            function will build an output space for you. The output dictionary depends on the derivates requested.
            A comprehensive list is provided below for each functional family.
                LDA:
                    EXC: zk
                    VXC: vrho
                    FXC: v2rho2
                    KXC: v3rho3
                    LXC: v4rho4
                GGA:
                    EXC: zk
                    VXC: vrho, vsigma
                    FXC: v2rho2, v2rhosigma, v2sigma2
                    KXC: v3rho3, v3rho2sigma, v3rhosigma2, v3sigma3
                    LXC: v4rho4, v4rho3sigma, v4rho2sigma2, v4rhosigma3, v4sigma4
                MGGA:
                    EXC: zk
                    VXC: vrho, vsigma, vlapl (optional), vtau
                    FXC: v2rho2, v2rhosigma, v2rholapl, v2rhotau, v2sigma2,
                         v2sigmalapl, v2sigmatau, v2lapl2, v2lapltau, v2tau2
                    KXC: v3rho3, v3rho2sigma, v3rho2lapl, v3rho2tau, v3rhosigma2,
                         v3rhosigmalapl, v3rhosigmatau, v3rholapl2, v3rholapltau,
                         v3rhotau2, v3sigma3, v3sigma2lapl, v3sigma2tau,
                         v3sigmalapl2, v3sigmalapltau, v3sigmatau2, v3lapl3,
                         v3lapl2tau, v3lapltau2, v3tau3
                    LXC: v4rho4, v4rho3sigma, v4rho3lapl, v4rho3tau, v4rho2sigma2,
                         v4rho2sigmalapl, v4rho2sigmatau, v4rho2lapl2, v4rho2lapltau,
                         v4rho2tau2, v4rhosigma3, v4rhosigma2lapl, v4rhosigma2tau,
                         v4rhosigmalapl2, v4rhosigmalapltau, v4rhosigmatau2,
                         v4rholapl3, v4rholapl2tau, v4rholapltau2, v4rhotau3,
                         v4sigma4, v4sigma3lapl, v4sigma3tau, v4sigma2lapl2,
                         v4sigma2lapltau, v4sigma2tau2, v4sigmalapl3, v4sigmalapl2tau,
                         v4sigmalapltau2, v4sigmatau3, v4lapl4, v4lapl3tau,
                         v4lapl2tau2, v4lapltau3, v4tau4

            For unpolarized functional the spin pieces are summed together.
            However, for polarized functionals the following order will be used for output quantities:
            (The last index is the fastest)

                VXC:
                    vrho         = (u, d)
                    vsigma       = (uu, ud, dd)
                    vlapl        = (u, d)
                    vtau         = (u, d)

                FXC:
                    v2rho2       = (u_u, u_d, d_d)
                    v2gamma2     = (uu_uu, uu_ud, uu_dd, ud_ud, ud_dd, dd_dd)
                    v2rhogamma   = (u_uu, u_ud, u_dd, d_uu, d_ud, d_dd)

                KXC:
                    v3rho2sigma  = (u_u_uu, u_u_ud, u_u_dd, u_d_uu, u_d_ud, u_d_dd, d_d_uu, d_d_ud, d_d_dd)
                    v3rhosigma2  = (u_uu_uu, u_uu_ud, u_uu_dd, u_ud_ud, u_ud_dd, u_dd_dd, d_uu_uu, d_uu_ud, d_uu_dd,
                                    d_ud_ud, d_ud_dd, d_dd_dd)
                    v3sigma      = (uu_uu_uu, uu_uu_ud, uu_uu_dd, uu_ud_ud, uu_ud_dd, uu_dd_dd, ud_ud_ud, ud_ud_dd,
                                    ud_dd_dd, dd_dd_dd)

        do_exc : bool (optional, True)
            Do evaluate the the functional?
        do_vxc : bool (optional, True)
            Do evaluate the derivative of the functional?
        do_fxc : bool (optional, False)
            Do evaluate the 2nd derivative of the functional?
        do_kxc : bool (optional, False)
            Do evaluate the 3rd derivative of the functional?
        do_lxc : bool (optional, False)
            Do evaluate the 4th derivative of the functional?

        Returns
        -------
        output : dict of array_like
            A dictionary of NumPy array-like structures. See the output section above for the expected returns.

        Examples
        --------

        # Build functional
        >>> func = pylibxc.LibXCFunctional("gga_c_pbe", "unpolarized")

        # Create input
        >>> inp = {}
        >>> inp["rho"] = np.random.random((3))
        >>> inp["sigma"] = np.random.random((3))

        # Compute
        >>> ret = func.compute(inp)
        >>> for k, v in ret.items():
        >>>     print(k, v)

        zk [[-0.06782171 -0.05452743 -0.04663709]]
        vrho [[-0.08349967 -0.0824188  -0.08054892]]
        vsigma [[ 0.00381277  0.00899967  0.01460601]]

        """

        # Check flags
        if not self._have_exc and do_exc:
            raise ValueError("Functional '%s' does not have EXC capabilities." % self.get_name())
        if not self._have_vxc and do_vxc:
            raise ValueError("Functional '%s' does not have VXC capabilities built in." % self.get_name())
        if not self._have_fxc and do_fxc:
            raise ValueError("Functional '%s' does not have FXC capabilities built in." % self.get_name())
        if not self._have_kxc and do_kxc:
            raise ValueError("Functional '%s' does not have KXC capabilities built in." % self.get_name())
        if not self._have_lxc and do_lxc:
            raise ValueError("Functional '%s' does not have LXC capabilities built in." % self.get_name())

        # Parse input arrays
        if hasattr(inp, "__array_interface__"):
            ns = array_backend.array_namespace(inp)
            inp = {"rho": ns.asarray(inp, dtype=ns.double)}
        elif isinstance(inp, dict):
            ns = array_backend.array_namespace(inp["rho"])
            inp = {k: ns.asarray(v, dtype=ns.double) for k, v in inp.items()}
        else:
            raise KeyError("Input must have a 'rho' variable or a single array.")

        # Brutal hack to get zeros on the same device as rho
        array_backend._zeros = lambda *args, **kwargs: ns.zeros_like(inp["rho"], *args, **kwargs)

        # How long are we?
        npoints = int(inp["rho"].size / self._spin)
        if (inp["rho"].size % self._spin):
            raise ValueError("Rho input has an invalid shape, must be divisible by %d" % self._spin)
        # Check the consistency of the input data
        if self._spin == 2:
            sizes = {"rho" : 2, "sigma" : 3, "tau" : 2, "lapl" : 2}
            for var in inp:
                if inp[var].size != sizes[var]*npoints:
                    raise ValueError(f"{var} input has an invalid shape, should have length {sizes[var]}*npoints")
        else:
            for var in inp:
                if inp[var].size != npoints:
                    raise ValueError(f"{var} input has an invalid shape, should have length npoints")

        # Find the right compute function
        args = [self.xc_func, ctypes.c_size_t(npoints)]
        if self.get_family() in [flags.XC_FAMILY_LDA, flags.XC_FAMILY_HYB_LDA]:
            input_labels   = ["rho"]
            args.extend([   inp[x] for x in  input_labels])
            input_num_args = 1

            output_labels = [
                "zk",       # 1, 1
                "vrho",     # 1, 2
                "v2rho2",   # 1, 3
                "v3rho3",   # 1, 4
                "v4rho4"    # 1, 5
            ]

            # Build input args
            output = _check_arrays(output, output_labels[0:1],
                            self.xc_func_sizes, npoints, do_exc)
            output = _check_arrays(output, output_labels[1:2],
                            self.xc_func_sizes, npoints, do_vxc)
            output = _check_arrays(output, output_labels[2:3],
                            self.xc_func_sizes, npoints, do_fxc)
            output = _check_arrays(output, output_labels[3:4],
                            self.xc_func_sizes, npoints, do_kxc)
            output = _check_arrays(output, output_labels[4:5],
                            self.xc_func_sizes, npoints, do_lxc)
            args.extend([output[x] for x in output_labels])

            core.xc_lda(*args)

        elif self.get_family() in [flags.XC_FAMILY_GGA, flags.XC_FAMILY_HYB_GGA]:
            input_labels   = ["rho", "sigma"]
            args.extend([   inp[x] for x in  input_labels])
            input_num_args = 2

            output_labels = [
                "zk",                                                               # 1, 1
                "vrho", "vsigma",                                                   # 2, 3
                "v2rho2", "v2rhosigma", "v2sigma2",                                 # 3, 6
                "v3rho3", "v3rho2sigma", "v3rhosigma2", "v3sigma3",                 # 4, 10
                "v4rho4", "v4rho3sigma", "v4rho2sigma2", "v4rhosigma3", "v4sigma4"  # 5, 15
            ]

            # Build input args
            output = _check_arrays(output, output_labels[0:1],
                            self.xc_func_sizes, npoints, do_exc)
            output = _check_arrays(output, output_labels[1:3],
                            self.xc_func_sizes, npoints, do_vxc)
            output = _check_arrays(output, output_labels[3:6],
                            self.xc_func_sizes, npoints, do_fxc)
            output = _check_arrays(output, output_labels[6:10],
                            self.xc_func_sizes, npoints, do_kxc)
            output = _check_arrays(output, output_labels[10:15],
                            self.xc_func_sizes, npoints, do_lxc)
            args.extend([output[x] for x in output_labels])

            core.xc_gga(*args)

        elif self.get_family() in [flags.XC_FAMILY_MGGA, flags.XC_FAMILY_HYB_MGGA]:
            # Build input args
            input_labels = ["rho", "sigma"]
            args.extend([   inp[x] for x in  input_labels])
            if self._needs_laplacian:
                input_labels.append("lapl")
                args.extend([inp["lapl"]])
            else:
                args.extend([ctypes.c_void_p(None)])  # Add none ptr for laplacian

            if self._needs_tau:
                input_labels.append("tau")
                args.extend([inp["tau"]])
            else:
                args.extend([ctypes.c_void_p(None)])  # Add none ptr for tau

            input_num_args = 4

            output_labels = [
                "zk",                                                                # 1, 1
                "vrho", "vsigma", "vlapl", "vtau",                                   # 4, 5
                "v2rho2", "v2rhosigma", "v2rholapl", "v2rhotau", "v2sigma2",         # 10, 15
                "v2sigmalapl", "v2sigmatau", "v2lapl2", "v2lapltau",  "v2tau2",
                "v3rho3", "v3rho2sigma", "v3rho2lapl", "v3rho2tau", "v3rhosigma2",   # 20, 35
                "v3rhosigmalapl", "v3rhosigmatau", "v3rholapl2", "v3rholapltau",
                "v3rhotau2", "v3sigma3", "v3sigma2lapl", "v3sigma2tau",
                "v3sigmalapl2", "v3sigmalapltau", "v3sigmatau2", "v3lapl3",
                "v3lapl2tau", "v3lapltau2", "v3tau3",
                "v4rho4", "v4rho3sigma", "v4rho3lapl", "v4rho3tau", "v4rho2sigma2",  # 35, 70
                "v4rho2sigmalapl", "v4rho2sigmatau", "v4rho2lapl2", "v4rho2lapltau",
                "v4rho2tau2", "v4rhosigma3", "v4rhosigma2lapl", "v4rhosigma2tau",
                "v4rhosigmalapl2", "v4rhosigmalapltau", "v4rhosigmatau2",
                "v4rholapl3", "v4rholapl2tau", "v4rholapltau2", "v4rhotau3",
                "v4sigma4", "v4sigma3lapl", "v4sigma3tau", "v4sigma2lapl2",
                "v4sigma2lapltau", "v4sigma2tau2", "v4sigmalapl3", "v4sigmalapl2tau",
                "v4sigmalapltau2", "v4sigmatau3", "v4lapl4", "v4lapl3tau",
                "v4lapl2tau2", "v4lapltau3", "v4tau4"
            ]

            # Build input args
            output = _check_arrays(output, output_labels[0:1],
                            self.xc_func_sizes, npoints, do_exc, self._needs_laplacian, self._needs_tau)
            output = _check_arrays(output, output_labels[1:5],
                            self.xc_func_sizes, npoints, do_vxc, self._needs_laplacian, self._needs_tau)
            output = _check_arrays(output, output_labels[5:15],
                            self.xc_func_sizes, npoints, do_fxc, self._needs_laplacian, self._needs_tau)
            output = _check_arrays(output, output_labels[15:35],
                            self.xc_func_sizes, npoints, do_kxc, self._needs_laplacian, self._needs_tau)
            output = _check_arrays(output, output_labels[35:70],
                            self.xc_func_sizes, npoints, do_lxc, self._needs_laplacian, self._needs_tau)
            args.extend([output[x] for x in output_labels])
            core.xc_mgga(*args)

        else:
            raise KeyError("Functional kind not recognized! (%d)" % self.get_kind())

        return {k: v for k, v in zip(output_labels, args[2+input_num_args:]) if v is not None}
