# Copyright (c) 2008-2019 MetPy Developers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import pint

units = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)

def masked_array(data, data_units=None, **kwargs):
    """Create a :class:`numpy.ma.MaskedArray` with units attached.

    This is a thin wrapper around :func:`numpy.ma.masked_array` that ensures that
    units are properly attached to the result (otherwise units are silently lost). Units
    are taken from the ``units`` argument, or if this is ``None``, the units on ``data``
    are used.

    Parameters
    ----------
    data : array_like
        The source data. If ``units`` is `None`, this should be a `pint.Quantity` with
        the desired units.
    data_units : str or `pint.Unit`
        The units for the resulting `pint.Quantity`
    **kwargs : Arbitrary keyword arguments passed to `numpy.ma.masked_array`

    Returns
    -------
    `pint.Quantity`

    """
    if data_units is None:
        data_units = data.units
    return units.Quantity(np.ma.masked_array(data, **kwargs), data_units)