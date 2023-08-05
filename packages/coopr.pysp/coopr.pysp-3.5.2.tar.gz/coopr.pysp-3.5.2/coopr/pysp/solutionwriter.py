#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['ISolutionWriterExtension']

from coopr.core.plugin import *


class ISolutionWriterExtension(Interface):

    def write(self, scenario_tree, output_file_prefix):
        """Called with a ScenarioTree type object."""
        pass
