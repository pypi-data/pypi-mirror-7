# -*- coding: utf-8 -*-
"""
MolVS - Molecule Validation and Standardization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MolVS is a python tool built on top of RDKit that performs validation and standardization of chemical structures.

:copyright: (c) 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import logging


__title__ = 'MolVS'
__version__ = '0.0.1'
__author__ = 'Matt Swain'
__email__ = 'm.swain@me.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014 Matt Swain'


from .standardize import Standardizer, standardize_smiles
from .errors import MolVSError, StandardizeError, ValidateError


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
