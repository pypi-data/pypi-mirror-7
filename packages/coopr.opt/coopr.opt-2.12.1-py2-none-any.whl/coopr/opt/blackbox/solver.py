#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

from coopr.opt.base import *


class COLINSolver(OptSolver):
    """An optimizer that can optimize the coopr.opt.colin.problem.OptProblem object"""

    def __init__(self, **kwds):
        """ Constructor """
        OptSolver.__init__(self,**kwds)
        self._valid_problem_formats=[ProblemFormat.colin_optproblem]
        self._valid_result_formats = {}
        self._valid_result_formats[ProblemFormat.colin_optproblem] = [ResultsFormat.osrl,ResultsFormat.results]
