import os
import glob

import numpy as np
import ctypes as ct

# or change this to your own path that contains libcgco.so
_CGCO_LIB_PATH = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
LIB_NAME = 'libcgco'

LIST_LIBGCO = glob.glob(os.path.join(_CGCO_LIB_PATH, LIB_NAME + '.*'))
assert len(LIST_LIBGCO) > 0, 'nothing found: %s' % repr(LIST_LIBGCO)
lib_exts = [os.path.splitext(os.path.basename(p))[1] for p in LIST_LIBGCO]
if '.so' in lib_exts:
    _CGCO_LIB_NAME = LIST_LIBGCO[lib_exts.index('.so')]
elif '.lib' in lib_exts:
    _CGCO_LIB_NAME = LIST_LIBGCO[lib_exts.index('.lib')]
elif '.dll' in lib_exts:
    _CGCO_LIB_NAME = LIST_LIBGCO[lib_exts.index('.dll')]
else:  # not sure what it found...
    print('found libs: %s' % repr([os.path.basename(p) for p in LIST_LIBGCO]))
    _CGCO_LIB_NAME = os.path.basename(LIST_LIBGCO[0])
assert os.path.exists(_CGCO_LIB_PATH), '%s' % _CGCO_LIB_PATH

# _CGCO_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# _CGCO_LIB_NAME = 'cgco'

# change the type definition depending on your machine and the compiled GCO library
_handle_type = ct.c_int
_handle_ptr_type = np.ctypeslib.ndpointer(dtype=np.intc)
_site_id_type = ct.c_int
_site_ptr_type = np.ctypeslib.ndpointer(dtype=np.intc)
_label_id_type = ct.c_int
_label_ptr_type = np.ctypeslib.ndpointer(dtype=np.intc)
_energy_term_type = ct.c_int
_energy_term_ptr_type = np.ctypeslib.ndpointer(dtype=np.intc)
# _energy_type = ct.c_int       # if energy32 is set
_energy_type = ct.c_longlong    # default type long long
# _energy_ptr_type = np.ctypeslib.ndpointer(dtype=np.intc)
_energy_ptr_type = np.ctypeslib.ndpointer(dtype=np.longlong)
_success_ptr_type = np.ctypeslib.ndpointer(dtype=np.intc)

_SMOOTH_COST_FN = ct.CFUNCTYPE(_energy_term_type, ct.c_int, ct.c_int,
                               _label_id_type, _label_id_type)

# load cgco shared library
_cgco = np.ctypeslib.load_library(_CGCO_LIB_NAME, _CGCO_LIB_PATH)

# declare the functions, argument types and return types
_cgco.gcoCreateGeneralGraph.argtypes = [_site_id_type, _label_id_type,
                                        _handle_ptr_type]
_cgco.gcoCreateGeneralGraph.restypes = ct.c_int

_cgco.gcoDestroyGraph.argtypes = [_handle_type]
_cgco.gcoDestroyGraph.restypes = ct.c_int

_cgco.gcoSetDataCost.argtypes = [_handle_type, _energy_term_ptr_type]
_cgco.gcoSetDataCost.restypes = ct.c_int

_cgco.gcoSetSiteDataCost.argtypes = [_handle_type, _site_id_type,
                                     _label_id_type, _energy_term_type]
_cgco.gcoSetSiteDataCost.restypes = ct.c_int

_cgco.gcoSetNeighborPair.argtypes = [_handle_type, _site_id_type,
                                     _site_id_type, _energy_term_type]
_cgco.gcoSetNeighborPair.restypes = ct.c_int

_cgco.gcoSetAllNeighbors.argtypes = [_handle_type, _site_ptr_type,
                                     _site_ptr_type, _energy_term_ptr_type,
                                     ct.c_int]
_cgco.gcoSetAllNeighbors.restypes = ct.c_int

_cgco.gcoSetSmoothCost.argtypes = [_handle_type, _energy_term_ptr_type]
_cgco.gcoSetSmoothCost.restype = ct.c_int

_cgco.gcoSetPairSmoothCost.argtypes = [_handle_type, _label_id_type,
                                       _label_id_type, _energy_term_type]
_cgco.gcoSetPairSmoothCost.restypes = ct.c_int

_cgco.gcoSetSmoothCostFunction.argtypes = [_handle_type, _SMOOTH_COST_FN]
_cgco.gcoSetSmoothCostFunction.restypes = ct.c_int

_cgco.gcoExpansion.argtypes = [_handle_type, ct.c_int, _energy_ptr_type]
_cgco.gcoExpansion.restypes = ct.c_int

_cgco.gcoExpansionOnAlpha.argtypes = [_handle_type, _label_id_type,
                                      _success_ptr_type]
_cgco.gcoExpansionOnAlpha.restypes = ct.c_int

_cgco.gcoSwap.argtypes = [_handle_type, ct.c_int, _energy_ptr_type]
_cgco.gcoSwap.restypes = ct.c_int

_cgco.gcoAlphaBetaSwap.argtypes = [_handle_type, _label_id_type, _label_id_type]
_cgco.gcoAlphaBetaSwap.restypes = ct.c_int

_cgco.gcoComputeEnergy.argtypes = [_handle_type, _energy_ptr_type]
_cgco.gcoComputeEnergy.restypes = ct.c_int

_cgco.gcoComputeDataEnergy.argtypes = [_handle_type, _energy_ptr_type]
_cgco.gcoComputeDataEnergy.restypes = ct.c_int

_cgco.gcoComputeSmoothEnergy.argtypes = [_handle_type, _energy_ptr_type]
_cgco.gcoComputeSmoothEnergy.restypes = ct.c_int

_cgco.gcoGetLabelAtSite.argtypes = [_handle_type, _site_id_type, _label_ptr_type]
_cgco.gcoGetLabelAtSite.restypes = ct.c_int

_cgco.gcoGetLabels.argtypes = [_handle_type, _label_ptr_type]
_cgco.gcoGetLabels.restype = ct.c_int

_cgco.gcoInitLabelAtSite.argtypes = [_handle_type, _site_id_type, _label_id_type]
_cgco.gcoInitLabelAtSite.restypes = ct.c_int
