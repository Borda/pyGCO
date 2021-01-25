import sys

import numpy as np
import ctypes as ct
try:
    from cgco import _cgco, _SMOOTH_COST_FN
except Exception:
    from .cgco import _cgco, _SMOOTH_COST_FN

# keep 4 effective digits for the fractional part if using real potentials
# make sure pairwise * smooth = unary so that the unary potentials and pairwise
# potentials are on the same scale.
_MAX_ENERGY_TERM_SCALE = 10000000
_UNARY_FLOAT_PRECISION = 100000
_PAIRWISE_FLOAT_PRECISION = 1000
_SMOOTH_COST_PRECISION = 100

_int_types = [np.int, np.intc, np.int32, np.int64, np.longlong]
if sys.platform == 'win32':
    _float_types = [np.float, np.float32, np.float64]
else:
    _float_types = [np.float, np.float32, np.float64, np.float128]

_SMALL_CONSTANT = 1e-10


# error classes
class PyGcoError(Exception):
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class ShapeMismatchError(PyGcoError):
    pass


class DataTypeNotSupportedError(PyGcoError):
    pass


class IndexOutOfBoundError(PyGcoError):
    pass


class GCO(object):
    def __init__(self):
        pass

    def create_general_graph(self, num_sites, num_labels, energy_is_float=False):
        """ Create a general graph with specified number of sites and labels.
        If energy_is_float is set to True, then automatic scaling and rounding
        will be applied to convert all energies to integers when running graph
        cuts. Then the final energy will be converted back to floats after the
        computation.

        :param num_sites:
        :param num_labels:
        :param energy_is_float:
        """
        self.temp_array = np.empty(1, dtype=np.intc)
        self.energy_temp_array = np.empty(1, dtype=np.longlong)
        _cgco.gcoCreateGeneralGraph(np.intc(num_sites), np.intc(num_labels),
                                    self.temp_array)

        self.handle = self.temp_array[0]
        self.nb_sites = np.intc(num_sites)
        self.nb_labels = np.intc(num_labels)
        self.energy_is_float = energy_is_float
        self.smooth_cost_fun = None

    def destroy_graph(self):
        _cgco.gcoDestroyGraph(self.handle)

    def _convert_unary_array(self, e):
        if self.energy_is_float:
            return (e * _UNARY_FLOAT_PRECISION).astype(np.intc)
        else:
            return e.astype(np.intc)

    def _convert_unary_term(self, e):
        if self.energy_is_float:
            return np.intc(e * _UNARY_FLOAT_PRECISION)
        else:
            return np.intc(e)

    def _convert_pairwise_array(self, e):
        if self.energy_is_float:
            return (e * _PAIRWISE_FLOAT_PRECISION).astype(np.intc)
        else:
            return e.astype(np.intc)

    def _convert_pairwise_term(self, e):
        if self.energy_is_float:
            return np.intc(e * _PAIRWISE_FLOAT_PRECISION)
        else:
            return np.intc(e)

    def _convert_smooth_cost_array(self, e):
        if self.energy_is_float:
            return (e * _SMOOTH_COST_PRECISION).astype(np.intc)
        else:
            return e.astype(np.intc)

    def _convert_smooth_cost_term(self, e):
        if self.energy_is_float:
            return np.intc(e * _SMOOTH_COST_PRECISION)
        else:
            return np.intc(e)

    def _convert_energy_back(self, e):
        if self.energy_is_float:
            return float(e) / _UNARY_FLOAT_PRECISION
        else:
            return e

    def set_data_cost(self, unary):
        """Set unary potentials, unary should be a matrix of size
        nb_sites x nb_labels. unary can be either integers or float"""

        if (self.nb_sites, self.nb_labels) != unary.shape:
            raise ShapeMismatchError(
                "Shape of unary potentials does not match the graph.")

        # Just a reference
        self._unary = self._convert_unary_array(unary)
        _cgco.gcoSetDataCost(self.handle, self._unary)

    def set_site_data_cost(self, site, label, e):
        """Set site data cost, dataCost(site, label) = e.
        e should be of type int or float (python primitive type)."""
        if site >= self.nb_sites or site < 0 or label < 0 \
                or label >= self.nb_labels:
            raise IndexOutOfBoundError()
        _cgco.gcoSetSiteDataCost(self.handle, np.intc(site), np.intc(label),
                                 self._convert_unary_term(e))

    def set_neighbor_pair(self, s1, s2, w):
        """Create an edge (s1, s2) with weight w.
        w should be of type int or float (python primitive type).
        s1 should be smaller than s2."""
        if not (0 <= s1 < s2 < self.nb_sites):
            raise IndexOutOfBoundError()
        _cgco.gcoSetNeighborPair(self.handle, np.intc(s1), np.intc(s2),
                                 self._convert_pairwise_term(w))

    def set_all_neighbors(self, s1, s2, w):
        """Setup the whole neighbor system in the graph.
        s1, s2, w are 1d numpy ndarrays of the same length.

        Each element in s1 should be smaller than the corresponding element in s2.
        """
        if s1.min() < 0 or s1.max() >= self.nb_sites or s2.min() < 0 \
                or s2.max() >= self.nb_sites:
            raise IndexOutOfBoundError()

        # These attributes are just used to keep a reference to corresponding
        # arrays, otherwise the temporarily used arrays will be destroyed by
        # python's garbage collection system, and the C++ library won't have
        # access to them any more, which may cause trouble.
        self._edge_s1 = s1.astype(np.intc)
        self._edge_s2 = s2.astype(np.intc)
        self._edge_w = self._convert_pairwise_array(w)

        _cgco.gcoSetAllNeighbors(self.handle, self._edge_s1, self._edge_s2,
                                 self._edge_w, np.intc(self._edge_s1.size))

    def set_smooth_cost(self, cost):
        """Set smooth cost. cost should be a symmetric numpy square matrix of
        size nb_labels x nb_labels.

        cost[l1, l2] is the cost of labeling l1 as l2 (or l2 as l1)
        """
        if cost.shape[0] != cost.shape[1] or (cost != cost.T).any():
            raise DataTypeNotSupportedError('Cost matrix not square or not symmetric')
        if cost.shape[0] != self.nb_labels:
            raise ShapeMismatchError('Cost matrix not of size nb_labels * nb_labels')

        # Just a reference
        self._smoothCost = self._convert_smooth_cost_array(cost)
        _cgco.gcoSetSmoothCost(self.handle, self._smoothCost)

    def set_pair_smooth_cost(self, l1, l2, cost):
        """Set smooth cost for a pair of labels l1, l2."""
        if not (0 <= l1 < self.nb_labels) or not (0 <= l2 < self.nb_labels):
            raise IndexOutOfBoundError()
        _cgco.gcoSetPairSmoothCost(self.handle, np.intc(l1), np.intc(l2),
                                   self._convert_smooth_cost_term(cost))

    def set_smooth_cost_function(self, fun):
        """Pass a function to calculate the smooth cost for sites s1 and s2 labeled l1 and l2.
            Function is of from fun (s1, s1, l1, l2) -> cost
        """
        def _typesafe(s1, s2, l1, l2):
            return self._convert_smooth_cost_term(fun(s1, s2, l1, l2))

        self.smooth_cost_fun = _SMOOTH_COST_FN(_typesafe)
        _cgco.gcoSetSmoothCostFunction(self.handle, self.smooth_cost_fun)

    def expansion(self, niters=-1):
        """Do alpha-expansion for specified number of iterations.
        Return total energy after the expansion moves.
        If niters is set to -1, the algorithm will run until convergence."""
        _cgco.gcoExpansion(self.handle, np.intc(niters), self.energy_temp_array)
        return self._convert_energy_back(self.energy_temp_array[0])

    def expansion_on_alpha(self, label):
        """Do one alpha-expansion move for the specified label.
        Return True if the energy decreases, return False otherwise."""
        if not (0 <= label < self.nb_labels):
            raise IndexOutOfBoundError()
        _cgco.gcoExpansionOnAlpha(self.handle, np.intc(label), self.temp_array)
        return self.temp_array[0] == 1

    def swap(self, niters=-1):
        """Do alpha-beta swaps for the specified number of iterations.
        Return total energy after the swap moves.
        If niters is set to -1, the algorithm will run until convergence."""
        _cgco.gcoSwap(self.handle, np.intc(niters), self.energy_temp_array)
        return self._convert_energy_back(self.energy_temp_array[0])

    def alpha_beta_swap(self, l1, l2):
        """Do a single alpha-beta swap for specified pair of labels."""
        if not (0 <= l1 < self.nb_labels) or not (0 <= l2 < self.nb_labels):
            raise IndexOutOfBoundError()
        _cgco.gcoAlphaBetaSwap(self.handle, np.intc(l1), np.intc(l2))

    def compute_energy(self):
        """Compute energy of current label assignments."""
        _cgco.gcoComputeEnergy(self.handle, self.energy_temp_array)
        return self._convert_energy_back(self.energy_temp_array[0])

    def compute_data_energy(self):
        """Compute the data energy of current label assignments."""
        _cgco.gcoComputeDataEnergy(self.handle, self.energy_temp_array)
        return self._convert_energy_back(self.energy_temp_array[0])

    def compute_smooth_energy(self):
        """Compute the smooth energy of current label assignments."""
        _cgco.gcoComputeSmoothEnergy(self.handle, self.energy_temp_array)
        return self._convert_energy_back(self.energy_temp_array[0])

    def get_label_at_site(self, site):
        """Get the current label assignment at a specified site."""
        if not (0 <= site < self.nb_sites):
            raise IndexOutOfBoundError()
        _cgco.gcoGetLabelAtSite(self.handle, np.intc(site), self.temp_array)
        return self.temp_array[0]

    def get_labels(self):
        """Get the full label assignment for the whole graph.
        Return a 1d vector of labels of length nb_sites.
        """
        labels = np.empty(self.nb_sites, dtype=np.intc)
        _cgco.gcoGetLabels(self.handle, labels)
        return labels

    def init_label_at_site(self, site, label):
        """Initialize label assignment at a specified site."""
        if not (0 <= site < self.nb_sites) or not (0 <= label < self.nb_labels):
            raise IndexOutOfBoundError()
        _cgco.gcoInitLabelAtSite(self.handle, np.intc(site), np.intc(label))


def cut_general_graph(edges, edge_weights, unary_cost, pairwise_cost=None,
                      n_iter=-1, algorithm='expansion', init_labels=None,
                      down_weight_factor=None):
    """
    Apply multi-label graph cuts to arbitrary graph given by `edges`.

    Parameters
    ----------
    edges: ndarray, int32, shape=(n_edges, 2)
        Rows correspond to edges in graph, given as vertex indices. The indices
        in the first column should always be smaller than corresponding indices
        from the second column.
    edge_weights: ndarray, int32 or float64, shape=(n_edges)
        Weights for each edge, listed in the same order as edges.
    unary_cost: ndarray, int32 or float64, shape=(n_vertices, n_labels)
        Unary potentials
    pairwise_cost: ndarray, int32 or float64, shape=(n_labels, n_labels)
        Pairwise potentials for label compatibility
    n_iter: int, (default=-1)
        Number of iterations. n_iter=-1 means run the algorithm until convergence.
    algorithm: string, `expansion` or `swap`, default=expansion
        Whether to perform alpha-expansion or alpha-beta-swaps.
    init_labels: ndarray, int32, shape=(n_vertices). Initial labels.
    down_weight_factor: float or None. Used to scale down the energy terms, so
        that they won't overflow once converted to integers. Default to None,
        where this factor is set automatically.

    Return
    ------
    labels: ndarray, int32, shape=(n_vertices) the resulting list of labels
        after optimization.

    Note all the node indices start from 0.

    >>> edges = np.array([(i, i + 1) for i in range(4)] + # first row
    ...                  [(i, i + 5) for i in range(5)] + # inter rows
    ...                  [(i, i + 1) for i in range(5, 9)]) # second row
    >>> weights = np.array([1] * len(edges))
    >>> unary = np.zeros((10, 2))
    >>> unary[5:, 0] = 1.
    >>> unary[:5, 1] = 1.
    >>> pairwise = (1 - np.eye(unary.shape[1])) * 0.5
    >>> labels = cut_general_graph(edges, weights, unary, pairwise)
    >>> labels  # doctest: +ELLIPSIS
    array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1]...)
    """
    energy_is_float = (unary_cost.dtype in _float_types) or \
        (edge_weights.dtype in _float_types) or \
        (pairwise_cost.dtype in _float_types)

    if not energy_is_float and not (
            (unary_cost.dtype in _int_types) and
            (edge_weights.dtype in _int_types) and
            (pairwise_cost.dtype in _int_types)):
        raise DataTypeNotSupportedError(
            "Unary and pairwise potentials should have consistent types. "
            "Either integers of floats. Mixed types or other types are not "
            "supported.")

    n_sites, n_labels = unary_cost.shape

    if down_weight_factor is None:
        down_weight_factor = max(np.abs(unary_cost).max(),
                                 np.abs(edge_weights).max() *
                                 pairwise_cost.max()) + _SMALL_CONSTANT

    gc = GCO()
    gc.create_general_graph(n_sites, n_labels, energy_is_float)
    gc.set_data_cost(unary_cost / down_weight_factor)
    gc.set_all_neighbors(edges[:, 0], edges[:, 1],
                         edge_weights / down_weight_factor)
    if pairwise_cost is not None:
        gc.set_smooth_cost(pairwise_cost)

    # initialize labels
    if init_labels is not None:
        for i in range(n_sites):
            gc.init_label_at_site(i, init_labels[i])

    if algorithm == 'expansion':
        gc.expansion(n_iter)
    else:
        gc.swap(n_iter)

    labels = gc.get_labels()
    gc.destroy_graph()

    return labels


def get_images_edges_vh(height, width):
    """ assuming uniform grid get vertical and horizontal edges

    :param int height: image height
    :param int width: image width
    :return: ndarray, ndarray, ndarray, ndarray

    >>> np.arange(2 * 3).reshape(2, 3)
    array([[0, 1, 2],
           [3, 4, 5]])
    >>> v_from, h_from, v_to, h_to = get_images_edges_vh(2, 3)
    >>> v_from
    array([0, 1, 2])
    >>> v_to
    array([3, 4, 5])
    >>> h_from
    array([0, 1, 3, 4])
    >>> h_to
    array([1, 2, 4, 5])
    """
    idxs = np.arange(height * width).reshape(height, width)
    v_edges_from = idxs[:-1, :].flatten()
    v_edges_to = idxs[1:, :].flatten()

    h_edges_from = idxs[:, :-1].flatten()
    h_edges_to = idxs[:, 1:].flatten()

    return v_edges_from, h_edges_from, v_edges_to, h_edges_to


def get_images_edges_diag(height, width):
    """ assuming uniform grid get diagonal edges:
    * top left -> bottom right
    * top right -> bottom left

    :param int height: image height
    :param int width: image width
    :return: ndarray, ndarray, ndarray, ndarray

    >>> np.arange(2 * 3).reshape(2, 3)
    array([[0, 1, 2],
           [3, 4, 5]])
    >>> dr_from, dl_from, dr_to, dl_to = get_images_edges_diag(2, 3)
    >>> dr_from
    array([0, 1])
    >>> dr_to
    array([4, 5])
    >>> dl_from
    array([1, 2])
    >>> dl_to
    array([3, 4])
    """
    idxs = np.arange(height * width).reshape(height, width)
    dr_edges_from = idxs[:-1, :-1].flatten()
    dr_edges_to = idxs[1:, 1:].flatten()

    dl_edges_to = idxs[1:, :-1].flatten()
    dl_edges_from = idxs[:-1, 1:].flatten()

    return dr_edges_from, dl_edges_from, dr_edges_to, dl_edges_to


def cut_grid_graph(unary_cost, pairwise_cost, cost_v, cost_h, cost_dr=None,
                   cost_dl=None, n_iter=-1, algorithm='expansion'):
    """
    Apply multi-label graphcuts to grid graph.

    Parameters
    ----------
    unary_cost: ndarray, int32, shape=(height, width, n_labels)
        Unary potentials
    pairwise_cost: ndarray, int32, shape=(n_labels, n_labels)
        Pairwise potentials for label compatibility
    cost_v: ndarray, int32, shape=(height-1, width)
        Vertical edge weights.
        cost_v[i,j] is the edge weight between (i,j) and (i+1,j)
    cost_h: ndarray, int32, shape=(height, width-1)
        Horizontal edge weights.
        cost_h[i,j] is the edge weight between (i,j) and (i,j+1)
    cost_dr: ndarray, int32, shape=(height-1, width-1)
        Diagonal edge weights.
        cost_dr[i,j] is the edge weight between (i,j) and (i+1,j+1)
    cost_dl: ndarray, int32, shape=(height-1, width-1)
        Diagonal edge weights.
        cost_dl[i,j] is the edge weight between (i,j+1) and (i+1,j)
    n_iter: int, (default=-1)
        Number of iterations.
        Set it to -1 will run the algorithm until convergence
    algorithm: string, `expansion` or `swap`, default=expansion
        Whether to perform alpha-expansion or alpha-beta-swaps.

    Note all the node indices start from 0.
    """
    energy_is_float = (unary_cost.dtype in _float_types) or \
                      (pairwise_cost.dtype in _float_types) or \
                      (cost_v.dtype in _float_types) or \
                      (cost_h.dtype in _float_types)

    if not energy_is_float and not (
        (unary_cost.dtype in _int_types) and
        (pairwise_cost.dtype in _int_types) and
            (cost_v.dtype in _int_types) and
            (cost_h.dtype in _int_types)):
        raise DataTypeNotSupportedError(
            "Unary and pairwise potentials should have consistent types. "
            "Either integers of floats. Mixed types or other types are not "
            "supported.")

    height, width, n_labels = unary_cost.shape

    gc = GCO()
    gc.create_general_graph(height * width, n_labels, energy_is_float)
    gc.set_data_cost(unary_cost.reshape([height * width, n_labels]))

    v_edges_from, h_edges_from, v_edges_to, h_edges_to = \
        get_images_edges_vh(height, width)
    v_edges_w = cost_v.flatten()
    assert len(v_edges_from) == len(v_edges_w), \
        'different sizes of edges %i and weights %i' \
        % (len(v_edges_from), len(v_edges_w))
    h_edges_w = cost_h.flatten()
    assert len(h_edges_from) == len(h_edges_w), \
        'different sizes of edges %i and weights %i' \
        % (len(h_edges_from), len(h_edges_w))

    edges_from = np.r_[v_edges_from, h_edges_from]
    edges_to = np.r_[v_edges_to, h_edges_to]
    edges_w = np.r_[v_edges_w, h_edges_w]

    if cost_dr is not None and cost_dl is not None:
        dr_edges_from, dl_edges_from, dr_edges_to, dl_edges_to = \
            get_images_edges_diag(height, width)
        dr_edges_w = cost_dr.flatten()
        assert len(dr_edges_from) == len(dr_edges_w), \
            'different sizes of edges %i and weights %i' \
            % (len(dr_edges_from), len(dr_edges_w))
        dl_edges_w = cost_dl.flatten()
        assert len(dl_edges_from) == len(dl_edges_w), \
            'different sizes of edges %i and weights %i' \
            % (len(dl_edges_from), len(dl_edges_w))

        edges_from = np.r_[edges_from, dr_edges_from, dl_edges_from]
        edges_to = np.r_[edges_to, dr_edges_to, dl_edges_to]
        edges_w = np.r_[edges_w, dr_edges_w, dl_edges_w]

    gc.set_all_neighbors(edges_from, edges_to, edges_w)

    gc.set_smooth_cost(pairwise_cost)

    if algorithm == 'expansion':
        gc.expansion(n_iter)
    else:
        gc.swap(n_iter)

    labels = gc.get_labels()
    gc.destroy_graph()

    return labels


def cut_grid_graph_simple(unary_cost, pairwise_cost, n_iter=-1,
                          connect=4, algorithm='expansion'):
    """
    Apply multi-label graphcuts to grid graph. This is a simplified version of
    cut_grid_graph, with all edge weights set to 1.

    Parameters
    ----------
    unary_cost: ndarray, int32, shape=(height, width, n_labels)
        Unary potentials
    pairwise_cost: ndarray, int32, shape=(n_labels, n_labels)
        Pairwise potentials for label compatibility
    connect: int, number of connected components - 4 or 8
    n_iter: int, (default=-1)
        Number of iterations.
        Set it to -1 will run the algorithm until convergence
    algorithm: string, `expansion` or `swap`, default=expansion
        Whether to perform alpha-expansion or alpha-beta-swaps.

    Note all the node indices start from 0.

    >>> annot = np.zeros((10, 10), dtype=int)
    >>> annot[:, 6:] = 2
    >>> annot[1:6, 3:8] = 1
    >>> annot
    array([[0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2]])
    >>> np.random.seed(0)
    >>> noise = np.random.randn(*annot.shape)
    >>> unary = np.tile(noise[:, :, np.newaxis], [1, 1, 3])
    >>> unary[:, :, 0] += 1 - (annot == 0)
    >>> unary[:, :, 1] += 1 - (annot == 1)
    >>> unary[:, :, 2] += 1 - (annot == 2)
    >>> pairwise = (1 - np.eye(3)) * 0.5
    >>> labels = cut_grid_graph_simple(unary, pairwise, n_iter=100)
    >>> labels.reshape(annot.shape).astype(int)
    array([[0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2]])
    >>> labels = cut_grid_graph_simple(unary, pairwise, connect=8, n_iter=100)
    >>> labels.reshape(annot.shape).astype(int)
    array([[0, 0, 0, 0, 1, 1, 1, 2, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 1, 1, 1, 1, 1, 2, 2],
           [0, 0, 0, 0, 1, 1, 1, 2, 2, 2],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
           [0, 0, 0, 0, 0, 0, 2, 2, 2, 2]])
    """
    height, width, n_labels = unary_cost.shape
    cost_v = np.ones((height - 1, width), dtype=unary_cost.dtype)
    cost_h = np.ones((height, width - 1), dtype=unary_cost.dtype)

    if connect == 8:
        cost_diag_dr = np.empty((height - 1, width - 1), dtype=unary_cost.dtype)
        cost_diag_dr.fill(np.sqrt(2))
        cost_diag_dl = np.empty((height - 1, width - 1), dtype=unary_cost.dtype)
        cost_diag_dl.fill(np.sqrt(2))
    else:
        cost_diag_dr, cost_diag_dl = None, None

    return cut_grid_graph(unary_cost, pairwise_cost, cost_v, cost_h,
                          cost_diag_dr, cost_diag_dl, n_iter, algorithm)
