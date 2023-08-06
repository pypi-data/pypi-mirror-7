#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['IPHExtension','IPHSolverServerExtension']

from coopr.core.plugin import *

# IMPORTANT: No variable fixing should occur until the post-iteration solves, following variable statistic updates.
#            Otherwise, variable statistics will not be correctly maintained.

class IPHExtension(Interface):

    def pre_ph_initialization(self,ph):
        """Called before PH initialization."""
        pass

    def post_instance_creation(self,ph):
        """Called after the instances have been created."""
        pass

    def post_ph_initialization(self, ph):
        """Called after PH initialization!"""
        pass

    def post_iteration_0_solves(self, ph):
        """Called after the iteration 0 solves!"""
        pass

    def post_iteration_0(self, ph):
        """Called after the iteration 0 solves, averages computation, and weight computation"""
        pass

    def pre_iteration_k_solves(self, ph):
        """Called before each iteration k solve"""
        pass

    def post_iteration_k_solves(self, ph):
        """Called after the iteration k solves!"""
        pass

    def post_iteration_k(self, ph):
        """Called after the iteration k is finished!"""
        pass

    def post_ph_execution(self, ph):
        """Called after PH has terminated!"""
        pass


class IPHSolverServerExtension(Interface):

    def pre_ph_initialization(self,ph):
        """Called before PH initialization."""
        pass

    def post_instance_creation(self,ph):
        """Called after the instances have been created."""
        pass

    def post_ph_initialization(self, ph):
        """Called after PH initialization!"""
        pass

    def pre_iteration_0_solve(self, ph):
        """Called before the iteration 0 solve begins!"""
        pass

    def post_iteration_0_solve(self, ph):
        """Called after the iteration 0 solve is finished!"""
        pass

    def pre_iteration_k_solve(self, ph):
        """Called before the iteration k solve begins!"""
        pass

    def post_iteration_k_solve(self, ph):
        """Called after the iteration k solve is finished!"""
        pass
