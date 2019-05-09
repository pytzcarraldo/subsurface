# Copyright (c) 2008-2019 MetPy Developers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import pint

units = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)


def check_units(*units_by_pos, **units_by_name):
    """Create a decorator to check units of function arguments."""
    try:
        from inspect import signature

        def dec(func):
            # Match the signature of the function to the arguments given to the decorator
            sig = signature(func)
            bound_units = sig.bind_partial(*units_by_pos, **units_by_name)

            # Convert our specified dimensionality (e.g. "[pressure]") to one used by
            # pint directly (e.g. "[mass] / [length] / [time]**2). This is for both efficiency
            # reasons and to ensure that problems with the decorator are caught at import,
            # rather than runtime.
            dims = {name: (orig, units.get_dimensionality(orig.replace('dimensionless', '')))
                    for name, orig in bound_units.arguments.items()}

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Match all passed in value to their proper arguments so we can check units
                bound_args = sig.bind(*args, **kwargs)
                bad = list(_check_argument_units(bound_args.arguments, dims))

                # If there are any bad units, emit a proper error message making it clear
                # what went wrong.
                if bad:
                    msg = '`{0}` given arguments with incorrect units: {1}.'.format(
                        func.__name__,
                        ', '.join('`{}` requires "{}" but given "{}"'.format(arg, req, given)
                                  for arg, given, req in bad))
                    if 'none' in msg:
                        msg += ('\nAny variable `x` can be assigned a unit as follows:\n'
                                '    from metpy.units import units\n'
                                '    x = x * units.meter / units.second')
                    raise ValueError(msg)
                return func(*args, **kwargs)

            return wrapper

    # signature() only available on Python >= 3.3, so for 2.7 we just do nothing.
    except ImportError:
        def dec(func):
            return func

    return dec