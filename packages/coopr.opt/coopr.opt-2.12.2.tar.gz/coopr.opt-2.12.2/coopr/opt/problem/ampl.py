#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

"""
Utilities to support the definition of optimization applications that
can be optimized with the Acro COLIN optimizers.
"""

__all__ = ['AmplModel']

import os
import re
import sys
from coopr.opt.base import ProblemFormat, convert_problem, guess_format
import coopr.opt
#from pyutilib.enum import Enum
#from coopr.core.plugin import *


class AmplModel(object):
    """
    A class that provides a wrapper for AMPL models.
    """

    def __init__(self, modfile, datfile=None):
        """
        The constructor.
        """
        self.modfile = modfile
        self.datfile = datfile

    def valid_problem_types(self):
        """This method allows the coopr.opt convert function to work with an AmplModel object."""
        return [ProblemFormat.mod]

    def _problem_files(self):
        if self.datfile is None:
            return [self.modfile]
        else:
            return [self.modfile, self.datfile]

    def write(self, filename, format=None, solver_capability=None):
        """
        Write the model to a file, with a given format.

        NOTE: this is the same exact code as is used in PyomoModel.py
        """
        if format is None and not filename is None:
            #
            # Guess the format if none is specified
            #
            format = guess_format(filename)
        if solver_capability is None:
            solver_capability = lambda x: True
        #
        if self.datfile is None:
            args = (self.modfile,)
        else:
            args = (self.modfile, self.datfile)
        res = convert_problem(args, format, [format], solver_capability)
        if not filename is None:
            os.rename(res[0][0], filename)

