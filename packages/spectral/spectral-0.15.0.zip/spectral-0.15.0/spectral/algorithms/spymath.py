#########################################################################
#
#   math.py - This file is part of the Spectral Python (SPy)
#   package.
#
#   Copyright (C) 2001-2013 Thomas Boggs
#
#   Spectral Python is free software; you can redistribute it and/
#   or modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   Spectral Python is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this software; if not, write to
#
#               Free Software Foundation, Inc.
#               59 Temple Place, Suite 330
#               Boston, MA 02111-1307
#               USA
#
#########################################################################
#
# Send comments to:
# Thomas Boggs, tboggs@users.sourceforge.net
#

'''
Miscellaneous math functions
'''

import numpy as np


def matrix_sqrt(X=None, symmetric=False, inverse=False, eigs=None):
    '''Returns the matrix square root of X.

    Arguments:

        `X` (square class::`numpy.ndarrray`)

        `symmetric` (bool, default False):

            If True, `X` is assumed to be symmetric, which speeds up
            calculation of the square root.

        `inverse` (bool, default False):

            If True, computes the matrix square root of inv(X).

        `eigs` (2-tuple):

            `eigs` must be a 2-tuple whose first element is an array of
            eigenvalues and whose second element is an ndarray of eigenvectors
            (individual eigenvectors are in columns). If this argument is
            provided, computation of the matrix square root is much faster. If
            this argument is provided, the `X` argument is ignored (in this
            case, it can be set to None).

    Returns a class::`numpy.ndarray` `S`, such that S.dot(S) = X
    '''
    if eigs is not None:
        (vals, V) = eigs
    else:
        (vals, V) = np.linalg.eig(X)
    k = len(vals)
    if inverse is False:
        SRV = np.diag(np.sqrt(vals))
    else:
        SRV = np.diag(1. / np.sqrt(vals))
    if symmetric:
        return V.dot(SRV).dot(V.T)
    else:
        return V.dot(SRV).dot(np.linalg.inv(V))

import exceptions

class NaNValueWarning(exceptions.UserWarning):
    pass

class NaNValueError(exceptions.ValueError):
    pass

def has_nan(X):
    '''returns True if ndarray `X` contains a NaN value.'''
    return bool(np.isnan(np.min(X)))
