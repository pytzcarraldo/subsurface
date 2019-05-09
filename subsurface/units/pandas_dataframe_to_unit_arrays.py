# Copyright (c) 2008-2019 MetPy Developers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import pint

units = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)

def pandas_dataframe_to_unit_arrays(df, column_units=None):
    """Attach units to data in pandas dataframes and return united arrays.

    Parameters
    ----------
    df : `pandas.DataFrame`
        Data in pandas dataframe.

    column_units : dict
        Dictionary of units to attach to columns of the dataframe. Overrides
        the units attribute if it is attached to the dataframe.

    Returns
    -------
        Dictionary containing united arrays with keys corresponding to the dataframe
        column names.

    """
    if not column_units:
        try:
            column_units = df.units
        except AttributeError:
            raise ValueError('No units attribute attached to pandas '
                             'dataframe and col_units not given.')

    # Iterate through columns attaching units if we have them, if not, don't touch it
    res = {}
    for column in df:
        if column in column_units and column_units[column]:
            res[column] = df[column].values * units(column_units[column])
        else:
            res[column] = df[column].values
    return res