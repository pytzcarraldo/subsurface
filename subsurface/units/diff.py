# Copyright (c) 2008-2019 MetPy Developers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import pint

units = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)

def diff(x, **kwargs):
    """Calculate the n-th discrete difference along given axis.

    Wraps :func:`numpy.diff` to handle units.

    Parameters
    ----------
    x : array-like
        Input data
    n : int, optional
        The number of times values are differenced.
    axis : int, optional
        The axis along which the difference is taken, default is the last axis.

    Returns
    -------
    diff : ndarray
        The n-th differences. The shape of the output is the same as `a`
        except along `axis` where the dimension is smaller by `n`. The
        type of the output is the same as that of the input.

    See Also
    --------
    numpy.diff

    """
    ret = np.diff(x, **kwargs)
    if hasattr(x, 'units'):
        # Can't just use units because of how things like temperature work
        it = x.flat
        true_units = (next(it) - next(it)).units
        ret = ret * true_units
    return ret