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
Define plugins used for defining OptProblem IO formats.
"""

from coopr.core.plugin import *

class IBlackBoxOptProblemIO(Interface):
    """An interface that defines reader/writer for a particular IO format"""

    def read(self, filename, point):
        """
        Read a point and request information.
        This method returns a tuple: point, requests
        """

    def write(self, filename, response):
        """
        Write response information to a file.
        """
