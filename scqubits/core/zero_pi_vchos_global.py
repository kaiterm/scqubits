import numpy as np

from scipy.special import comb

from scqubits.core import descriptors
from scqubits.core.zero_pi_vchos import ZeroPiVCHOS
from scqubits.core.hashing import Hashing


# -Zero-Pi using VCHOS and a global cutoff

class ZeroPiVCHOSGlobal(ZeroPiVCHOS, Hashing):
    global_exc = descriptors.WatchedProperty('QUANTUMSYSTEM_UPDATE')

    def __init__(self, EJ, EL, ECJ, EC, ng, flux, kmax, global_exc, dEJ=0, dCJ=0, truncated_dim=None):
        ZeroPiVCHOS.__init__(self, EJ, EL, ECJ, EC, ng, flux, kmax, num_exc=None,
                             dEJ=dEJ, dCJ=dCJ, truncated_dim=truncated_dim)
        Hashing.__init__(self)
        self._sys_type = type(self).__name__
        self.global_exc = global_exc

    @staticmethod
    def default_params():
        return {
            'EJ': 10.0,
            'EL': 0.04,
            'ECJ': 20.0,
            'EC': 0.04,
            'dEJ': 0.0,
            'dCJ': 0.0,
            'ng': 0.1,
            'flux': 0.23,
            'global_exc': 5,
            'truncated_dim': 10
        }

    @staticmethod
    def nonfit_params():
        return ['ng', 'flux', 'global_exc', 'truncated_dim']

    def a_operator(self, i):
        """
        This method for defining the a_operator is based on
        J. M. Zhang and R. X. Dong, European Journal of Physics 31, 591 (2010).
        We ask the question, for each basis vector, what is the action of a_i
        on it? In this way, we can define a_i using a single for loop.
        """
        basis_vecs = self._gen_basis_vecs()
        tags, index_array = self._gen_tags(basis_vecs)
        dim = basis_vecs.shape[0]
        a = np.zeros((dim, dim))
        for w, vec in enumerate(basis_vecs):
            if vec[i] >= 1:
                temp_vec = np.copy(vec)
                temp_vec[i] = vec[i] - 1
                temp_coeff = np.sqrt(vec[i])
                temp_vec_tag = self._hash(temp_vec)
                index = np.searchsorted(tags, temp_vec_tag)
                basis_index = index_array[index]
                a[basis_index, w] = temp_coeff
        return a

    def number_states_per_minimum(self):
        """
        Using the global excitation scheme the total number of states
        per minimum is given by the hockey-stick identity
        """
        return int(comb(self.global_exc + self.number_degrees_freedom(), self.number_degrees_freedom()))
