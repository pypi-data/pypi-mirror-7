#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NTSC RGB Colourspace
====================

Defines the *NTSC RGB* colourspace:

-   :attr:`NTSC_RGB_COLOURSPACE`.

See Also
--------
`RGB Colourspaces IPython Notebook
<http://nbviewer.ipython.org/github/colour-science/colour-ipython/blob/master/notebooks/models/rgb.ipynb>`_  # noqa

References
----------
.. [1]  `Recommendation ITU-R BT.470-6 - Conventional Television Systems
        <http://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.470-6-199811-S!!PDF-E.pdf>`_  # noqa
        (Last accessed 13 April 2014)
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

__all__ = ['NTSC_RGB_PRIMARIES',
           'NTSC_RGB_WHITEPOINT',
           'NTSC_RGB_TO_XYZ_MATRIX',
           'XYZ_TO_NTSC_RGB_MATRIX',
           'NTSC_RGB_TRANSFER_FUNCTION',
           'NTSC_RGB_INVERSE_TRANSFER_FUNCTION',
           'NTSC_RGB_COLOURSPACE']

NTSC_RGB_PRIMARIES = np.array(
    [[0.67, 0.33],
     [0.21, 0.71],
     [0.14, 0.08]])
"""
*NTSC RGB* colourspace primaries.

NTSC_RGB_PRIMARIES : ndarray, (3, 2)
"""

NTSC_RGB_WHITEPOINT = ILLUMINANTS.get(
    'CIE 1931 2 Degree Standard Observer').get('C')
"""
*NTSC RGB* colourspace whitepoint.

NTSC_RGB_WHITEPOINT : tuple
"""

NTSC_RGB_TO_XYZ_MATRIX = normalised_primary_matrix(NTSC_RGB_PRIMARIES,
                                                   NTSC_RGB_WHITEPOINT)
"""
*NTSC RGB* colourspace to *CIE XYZ* colourspace matrix.

NTSC_RGB_TO_XYZ_MATRIX : array_like, (3, 3)
"""

XYZ_TO_NTSC_RGB_MATRIX = np.linalg.inv(NTSC_RGB_TO_XYZ_MATRIX)
"""
*CIE XYZ* colourspace to *NTSC RGB* colourspace matrix.

XYZ_TO_NTSC_RGB_MATRIX : array_like, (3, 3)
"""

NTSC_RGB_TRANSFER_FUNCTION = lambda x: x ** (1 / 2.2)
"""
Transfer function from linear to *NTSC RGB* colourspace.

NTSC_RGB_TRANSFER_FUNCTION : object
"""

NTSC_RGB_INVERSE_TRANSFER_FUNCTION = lambda x: x ** 2.2
"""
Inverse transfer function from *NTSC RGB* colourspace to linear.

NTSC_RGB_INVERSE_TRANSFER_FUNCTION : object
"""

NTSC_RGB_COLOURSPACE = RGB_Colourspace(
    'NTSC RGB',
    NTSC_RGB_PRIMARIES,
    NTSC_RGB_WHITEPOINT,
    NTSC_RGB_TO_XYZ_MATRIX,
    XYZ_TO_NTSC_RGB_MATRIX,
    NTSC_RGB_TRANSFER_FUNCTION,
    NTSC_RGB_INVERSE_TRANSFER_FUNCTION)
"""
*NTSC RGB* colourspace.

NTSC_RGB_COLOURSPACE : RGB_Colourspace
"""
