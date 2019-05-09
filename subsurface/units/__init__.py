# Copyright (c) 2008-2019 MetPy Developers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause
r"""Module to provide unit support.

This makes use of the :mod:`pint` library and sets up the default settings
for good temperature support.

Attributes
----------
units : :class:`pint.UnitRegistry`
    The unit registry used throughout the package. Any use of units in MetPy should
    import this registry and use it to grab units.

"""

from __future__ import division

import functools
import logging

import numpy as np
import pint
import pint.unit

__all__ = ["check_units", "concatenate", "diff", "masked_array", "pandas_datagrame_to_unit_array"]

log = logging.getLogger(__name__)

UndefinedUnitError = pint.UndefinedUnitError
DimensionalityError = pint.DimensionalityError

units = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)

# For pint 0.6, this is the best way to define a dimensionless unit. See pint #185
units.define(pint.unit.UnitDefinition('percent', '%', (),
             pint.converters.ScaleConverter(0.01)))

# Define commonly encountered units not defined by pint
units.define('degrees_north = degree = degrees_N = degreesN = degree_north = degree_N '
             '= degreeN')
units.define('degrees_east = degree = degrees_E = degreesE = degree_east = degree_E = degreeE')
units.define('us_feet = usft = usfeet = 30.4801 cm')
units.define('us_barrel = usbbl = us_bbl = usbbl = 119.240471 liters')
units.define('BTU = 1055.05585262 Joule')
units.define('API = (bbl / metric_ton * 141.5 * 0.159) - 131.5 = API_gravity ')

# Alias geopotential meters (gpm) to just meters
try:
    units._units['meter']._aliases = ('metre', 'gpm')
    units._units['gpm'] = units._units['meter']
except AttributeError:
    log.warning('Failed to add gpm alias to meters.')

def _check_argument_units(args, dimensionality):
    """Yield arguments with improper dimensionality."""
    for arg, val in args.items():
        # Get the needed dimensionality (for printing) as well as cached, parsed version
        # for this argument.
        try:
            need, parsed = dimensionality[arg]
        except KeyError:
            # Argument did not have units specified in decorator
            continue

        # See if the value passed in is appropriate
        try:
            if val.dimensionality != parsed:
                yield arg, val.units, need
        # No dimensionality
        except AttributeError:
            # If this argument is dimensionless, don't worry
            if parsed != '':
                yield arg, 'none', need

try:
    # Try to enable pint's built-in support
    units.setup_matplotlib()
except (AttributeError, RuntimeError):  # Pint's not available, try to enable our own
    import matplotlib.units as munits

    # Inheriting from object fixes the fact that matplotlib 1.4 doesn't
    # TODO: Remove object when we drop support for matplotlib 1.4
    class PintAxisInfo(munits.AxisInfo, object):
        """Support default axis and tick labeling and default limits."""

        def __init__(self, units):
            """Set the default label to the pretty-print of the unit."""
            super(PintAxisInfo, self).__init__(label='{:P}'.format(units))

    # TODO: Remove object when we drop support for matplotlib 1.4
    class PintConverter(munits.ConversionInterface, object):
        """Implement support for pint within matplotlib's unit conversion framework."""

        def __init__(self, registry):
            """Initialize converter for pint units."""
            super(PintConverter, self).__init__()
            self._reg = registry

        def convert(self, value, unit, axis):
            """Convert :`Quantity` instances for matplotlib to use."""
            if isinstance(value, (tuple, list)):
                return [self._convert_value(v, unit, axis) for v in value]
            else:
                return self._convert_value(value, unit, axis)

        def _convert_value(self, value, unit, axis):
            """Handle converting using attached unit or falling back to axis units."""
            if hasattr(value, 'units'):
                return value.to(unit).magnitude
            else:
                return self._reg.Quantity(value, axis.get_units()).to(unit).magnitude

        @staticmethod
        def axisinfo(unit, axis):
            """Return axis information for this particular unit."""
            return PintAxisInfo(unit)

        @staticmethod
        def default_units(x, axis):
            """Get the default unit to use for the given combination of unit and axis."""
            if isinstance(x, (tuple, list)):
                return getattr(x[0], 'units', 'dimensionless')
            else:
                return getattr(x, 'units', 'dimensionless')

    # Register the class
    munits.registry[units.Quantity] = PintConverter(units)
    del munits
del pint