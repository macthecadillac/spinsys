"""This module provides functions working on half-spin systems.
Functions included:
    create_complete_basis
    full_matrix
    reorder_basis
    similarity_trans_matrix

1-16-2017
"""

import numpy as np
import scipy as sp
from spinsys import utils


def create_complete_basis(N, current_j):
    """Creates a complete basis for the current total <Sz>"""
    dim = 2 ** N
    spin_ups = int(round(0.5 * N + current_j))
    spin_downs = N - spin_ups
    blksize = int(round(sp.misc.comb(N, spin_ups)))
    basis_seed = [0] * spin_downs + [1] * spin_ups
    basis = basis_seed
    # "to_diag" is a dict that maps ordinary indices to block diagonalized
    #  indices. "to_ord" is the opposite.
    basis_set, to_diag, to_ord = [], {}, {}
    for i in range(blksize):
        try:
            basis = utils.misc.binary_permutation(basis)
        except IndexError:                # When current_j is N // 2 or -N // 2
            pass
        basis_set.append(basis[:])
        decimal_basis = utils.misc.bin_to_dec(basis)
        # i is the index within only this block
        to_diag[dim - decimal_basis - 1] = i
        to_ord[i] = dim - decimal_basis - 1
    return basis_set, to_diag, to_ord


def full_matrix(matrix, k, N):
    """
    Builds the S matrices in an N particle system. Assumes periodic boundary
    condition.
    "S" could be an operator/state we want to work on. If it is a state, it
    must be put in a column vector form. "S" must be sparse.
    "k" is the location index of the particle in a particle chain. The first
    particle has k=0, the second has k=1 and so on.
    Returns a sparse matrix.
    """
    dim = 2
    if not sp.sparse.issparse(matrix):
        S = sp.sparse.csc_matrix(matrix)
    else:
        S = matrix
    if k == 0:
        S_full = sp.sparse.kron(S, sp.sparse.eye(dim ** (N - 1)))
    elif k == 1:
        S_full = sp.sparse.eye(dim)
        S_full = sp.sparse.kron(S_full, S)
        S_full = sp.sparse.kron(S_full, sp.sparse.eye(dim ** (N - 2)))
    else:
        S_full = sp.sparse.eye(dim)
        S_full = sp.sparse.kron(S_full, sp.sparse.eye(dim ** (k - 1)))
        S_full = sp.sparse.kron(S_full, S)
        S_full = sp.sparse.kron(S_full, sp.sparse.eye(dim ** (N - k - 1)))

    return S_full


def reorder_basis(N, psi_diag, current_j=0):
    """
    Reorders the basis of a vector from one arranged by their total <Sz>
    to one that results from tensor products.

    Args: "N" System size
          "psi_diag" State in a block diagonalized basis arrangement
          "current_j" Total <Sz>
    Returns: Numpy 2D array (column vector)
    """
    psi_ord = np.zeros([2 ** N, 1], complex)
    to_ord = create_complete_basis(N, current_j)[2]
    try:
        for i in psi_diag.nonzero()[0]:
            psi_ord[to_ord[i], 0] = psi_diag[i, 0]
    # The except suite provides compatibility with 1-D Numpy vectors
    except IndexError:
        for i in psi_diag.nonzero()[0]:
            psi_ord[to_ord[i], 0] = psi_diag[i]
    return psi_ord


def similarity_trans_matrix(N):
    """
    Returns a matrix U such that Uv = v' with v in the tensor product
    basis arrangement and v' in the spin block basis arrangement.

    Args: "N" System size
    Returns: Sparse matrix (CSC matrix)
    """
    offset = 0
    dim = 2 ** N
    data = np.ones(dim)
    row_ind = np.empty(dim)
    col_ind = np.empty(dim)
    current_pos = 0                     # current position along the data array
    for current_j in np.arange(N / 2, -N / 2 - 1, -1):
        spin_ups = round(0.5 * N + current_j)
        blksize = int(round(sp.misc.comb(N, spin_ups)))
        to_diag = create_complete_basis(N, current_j)[1]
        for ord_ind, diag_ind in to_diag.items():
            row_ind[current_pos] = diag_ind + offset
            col_ind[current_pos] = ord_ind
            current_pos += 1
        offset += blksize
    return sp.sparse.csc_matrix((data, (row_ind, col_ind)), shape=(dim, dim))
