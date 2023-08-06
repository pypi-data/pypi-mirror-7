#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Max RGB Colourspace
===================

Defines the *Max RGB* colourspace:

-   :attr:`MAX_RGB_COLOURSPACE`.

See Also
--------
`RGB Colourspaces IPython Notebook
<http://nbviewer.ipython.org/github/colour-science/colour-ipython/blob/master/notebooks/models/rgb.ipynb>`_  # noqa

References
----------
.. [1]  http://www.hutchcolor.com/profiles/MaxRGB.zip
        (Last accessed 12 April 2014)
"""

from __future__ import division, unicode_literals

import numpy as np

from colour.colorimetry import ILLUMINANTS
from colour.models import RGB_Colourspace, normalised_primary_matrix

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2014 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['MAX_RGB_PRIMARIES',
           'MAX_RGB_WHITEPOINT',
           'MAX_RGB_TO_XYZ_MATRIX',
           'XYZ_TO_MAX_RGB_MATRIX',
           'MAX_RGB_TRANSFER_FUNCTION',
           'MAX_RGB_INVERSE_TRANSFER_FUNCTION',
           'MAX_RGB_COLOURSPACE']

MAX_RGB_PRIMARIES = np.array(
    [[0.73413379, 0.26586621],
     [0.10039113, 0.89960887],
     [0.03621495, 0.00000000]])
"""
*Max RGB* colourspace primaries.

MAX_RGB_PRIMARIES : ndarray, (3, 2)
"""

MAX_RGB_WHITEPOINT = ILLUMINANTS.get(
    'CIE 1931 2 Degree Standard Observer').get('D50')
"""
*Max RGB* colourspace whitepoint.

MAX_RGB_WHITEPOINT : tuple
"""

MAX_RGB_TO_XYZ_MATRIX = normalised_primary_matrix(MAX_RGB_PRIMARIES,
                                                  MAX_RGB_WHITEPOINT)
"""
*Max RGB* colourspace to *CIE XYZ* colourspace matrix.

MAX_RGB_TO_XYZ_MATRIX : array_like, (3, 3)
"""

XYZ_TO_MAX_RGB_MATRIX = np.linalg.inv(MAX_RGB_TO_XYZ_MATRIX)
"""
*CIE XYZ* colourspace to *Max RGB* colourspace matrix.

XYZ_TO_MAX_RGB_MATRIX : array_like, (3, 3)
"""

MAX_RGB_TRANSFER_FUNCTION = lambda x: x ** (1 / 2.2)
"""
Transfer function from linear to *Max RGB* colourspace.

MAX_RGB_TRANSFER_FUNCTION : object
"""

MAX_RGB_INVERSE_TRANSFER_FUNCTION = lambda x: x ** 2.2
"""
Inverse transfer function from *Max RGB* colourspace to linear.

MAX_RGB_INVERSE_TRANSFER_FUNCTION : object
"""

MAX_RGB_COLOURSPACE = RGB_Colourspace(
    'Max RGB',
    MAX_RGB_PRIMARIES,
    MAX_RGB_WHITEPOINT,
    MAX_RGB_TO_XYZ_MATRIX,
    XYZ_TO_MAX_RGB_MATRIX,
    MAX_RGB_TRANSFER_FUNCTION,
    MAX_RGB_INVERSE_TRANSFER_FUNCTION)
"""
*Max RGB* colourspace.

MAX_RGB_COLOURSPACE : RGB_Colourspace
"""
