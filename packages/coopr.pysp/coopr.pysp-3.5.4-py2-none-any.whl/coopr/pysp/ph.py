#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import copy
import gc
import logging
import pickle
import sys
import traceback
import types
import time
import types
import inspect

from math import fabs, log, exp
from os import path

from six import iterkeys, itervalues, iteritems, advance_iterator

from coopr.opt import SolverResults, SolverStatus, UndefinedData, ProblemFormat, undefined
from coopr.opt.base import SolverFactory
from coopr.opt.parallel import SolverManagerFactory
from coopr.pyomo import *
from coopr.pyomo.base import BasicSymbolMap, CounterLabeler
from coopr.pysp.phextension import IPHExtension
from coopr.pysp.ef import create_ef_instance
from coopr.pysp.generators import scenario_tree_node_variables_generator, \
                                  scenario_tree_node_variables_generator_noinstances
from coopr.pysp.phsolverserverutils import *
from coopr.pysp.phsolverserverutils import TransmitType

from coopr.pysp.phutils import *
from coopr.pysp.phobjective import *
from coopr.pysp.scenariotree import *
from coopr.pysp.dualphmodel import DualPHModel
import coopr.solvers.plugins.smanager.phpyro

from coopr.core.plugin import ExtensionPoint

try:
    from guppy import hpy
    guppy_available = True
except ImportError:
    guppy_available = False

logger = logging.getLogger('coopr.pysp')

# PH iteratively solves scenario sub-problems, so we don't want to
# waste a ton of time preprocessing unless some specific aspects of
# the scenario instances change.  for example, a variable was fixed,
# the objective was modified, or constraints were added. and if
# instances do change, we only want to do the minimal amount of work
# to get the instance back to a consistent "preprocessed" state.  the
# following attributes are introduced to help perform the minimal
# amount of work, and should be augmented in the future if we can
# somehow do less.  these attributes are initially cleared, and are
# re-set - following preprocessing, if necessary - at the top of the
# PH iteration loop. this gives a chance for plugins and linearization
# to get a chance at modification, and to set the appropriate
# attributes so that the instances can be appropriately preprocessed
# before solves for the next iteration commence. we assume (by
# prefixing the attribute name with "instance") that modifications of
# the indicated type have been uniformly applied to all instances.
class ProblemStates(object):

    #def __getstate__(self):
    #    return dict(self.__slots__)

    def __init__(self, instances):

        # ph objects added to each model
        self.has_ph_objective_weight_terms = dict.fromkeys(instances, False)
        self.has_ph_objective_proximal_terms = dict.fromkeys(instances, False)
        self.ph_objective_proximal_expressions = dict.fromkeys(instances, None)
        self.ph_objective_weight_expressions = dict.fromkeys(instances, None)
        self.ph_constraints = dict((inst_name,[]) for inst_name in instances)
        self.ph_variables = dict((inst_name,[]) for inst_name in instances)

        # TODO: Reconcile this new method with the persistent solver plugin
        """
        # keeps track of instances with recently fixed or freed variables
        self.fixed_variables = dict.fromkeys(instances, False)
        self.freed_variables = dict.fromkeys(instances, False)
        """
        # maps between instance name and a list of (variable-name, index) pairs
        self.fixed_variables = dict((inst_name,[]) for inst_name in instances)
        self.freed_variables = dict((inst_name,[]) for inst_name in instances)

        # just coefficients modified
        self.objective_updated = dict.fromkeys(instances, False)
        self.ph_constraints_updated = dict.fromkeys(instances, False)
        self.user_constraints_updated = dict.fromkeys(instances, False)

    def clear_update_flags(self,name=None):
        if name is not None:
            self.objective_updated[name] = False
            self.ph_constraints_updated[name] = False
            self.user_constraints_updated[name] = False
        else:
            for key in iterkeys(self.objective_updated):
                self.objective_updated[key] = False
            for key in iterkeys(self.ph_constraints_updated):
                self.ph_constraints_updated[key] = False
            for key in iterkeys(self.user_constraints_updated):
                self.user_constraints_updated[key] = False

    # TODO
    """
    def has_fixed_variables(self,name=None):
        if name is None:
            for val in itervalues(self.fixed_variables):
                if val:
                    return True
            return False
        else:
            return self.fixed_variables[name]

    def has_freed_variables(self,name=None):
        if name is None:
            for val in itervalues(self.freed_variables):
                if val:
                    return True
            return False
        else:
            return self.freed_variables[name]
    """
    def has_fixed_variables(self,name=None):
        if name is None:
            for val in itervalues(self.fixed_variables):
                if len(val) > 0:
                    return True
            return False
        else:
            return len(self.fixed_variables[name]) > 0

    def has_freed_variables(self,name=None):
        if name is None:
            for val in itervalues(self.freed_variables):
                if len(val) > 0:
                    return True
            return False
        else:
            return len(self.freed_variables[name]) > 0

    def has_ph_constraints(self,name=None):
        if name is None:
            for val in itervalues(self.ph_constraints):
                if len(val) > 0:
                    return True
            return False
        else:
            return len(self.ph_constraints[name]) > 0

    def has_ph_variables(self,name=None):
        if name is None:
            for val in itervalues(self.ph_variables):
                if len(val) > 0:
                    return True
            return False
        else:
            return len(self.ph_variables[name]) > 0
    
    # TODO
    """
    def clear_fixed_variables(self, name=None):
        if name is None:
            for key in self.fixed_variables:
                self.fixed_variables[key] = False
        else:
            if name in self.fixed_variables:
                self.fixed_variables[name] = False
            else:
                raise KeyError("KeyError: %s" % name)   
 
    def clear_freed_variables(self, name=None):
        if name is None:
            for key in self.freed_variables:
                self.freed_variables[key] = False
        else:
            if name in self.freed_variables:
                self.freed_variables[name] = False
            else:
                raise KeyError("KeyError: %s" % name)
    """

    def clear_fixed_variables(self, name=None):
        if name is None:
            for key in self.fixed_variables:
                self.fixed_variables[key] = []
        else:
            if name in self.fixed_variables:
                self.fixed_variables[name] = []
            else:
                raise KeyError("KeyError: %s" % name)

    def clear_freed_variables(self, name=None):
        if name is None:
            for key in self.freed_variables:
                self.freed_variables[key] = []
        else:
            if name in self.freed_variables:
                self.freed_variables[name] = []
            else:
                raise KeyError("KeyError: %s" % name)

    def clear_ph_variables(self, name=None):
        if name is None:
            for key in self.ph_variables:
                self.ph_variables[key] = []
        else:
            if name in self.ph_variables:
                self.ph_variables[name] = []
            else:
                raise KeyError("KeyError: %s" % name)

    def clear_ph_constraints(self, name=None):
        if name is None:
            for key in self.ph_constraints:
                self.ph_constraints[key] = []
        else:
            if name in self.ph_constraints:
                self.ph_constraints[name] = []
            else:
                raise KeyError("KeyError: %s" % name)

class AggregateUserData(object):
    pass

    @staticmethod
    def assign_aggregate_data(fakeself,
                              scenario_tree,
                              scenario_tree_object,
                              aggregate_data):
        fakeself._aggregate_user_data = aggregate_data

class _PHBase(object):

    def __init__(self):

        # PH solver information / objects.
        self._solver = None
        self._solver_type = "cplex"
        self._solver_io = None
        self._comparison_tolerance_for_fixed_vars = 1e-5

        self._problem_states = None

        # a flag indicating whether we preprocess constraints in our
        # scenario instances when variables are fixed/freed, or
        # whether we simply write the bounds while presenting the
        # instances to solvers.
        self._write_fixed_variables = True
        self._fix_queue = {}

        # For the users to modify as they please in the aggregate
        # callback as long as the data placed on it can be pickled
        self._aggregate_user_data = AggregateUserData()

        # maps scenario name to the corresponding model instance
        self._instances = {} 

        # for various reasons (mainly hacks at this point), it's good
        # to know whether we're minimizing or maximizing.
        self._objective_sense = None

        # maps scenario name to the last gap reported by the solver
        # when solving the associated instance. if there is no entry,
        # then there has been no solve.
        # NOTE: This dictionary could expand significantly, as we
        #       identify additional solve-related information
        #       associated with an instance.
        self._gaps = {}

        # maps scenario name to the last solve time reported for the 
        # corresponding scenario sub-problem.
        self._solve_times = {}

        # all information related to the scenario tree (implicit and
        # explicit).
        self._model = None # not instantiated

        # defines the stochastic program structure and links in that
        # structure with the scenario instances (e.g., _VarData
        # objects).
        self._scenario_tree = None

        # there are situations in which it is valuable to snapshot /
        # store the solutions associated with the scenario
        # instances. for example, when one wants to use a warm-start
        # from a particular iteration solve, following a modification
        # and re-solve of the problem instances in a user-defined
        # callback. the following nested dictionary is intended to
        # serve that purpose. The nesting is dependent on whether
        # bundling and or phpyro is in use
        self._cached_solutions = {}

        # PH reporting parameters

        # do I flood the screen with status output?
        self._verbose = False
        self._output_times = False

        # PH configuration parameters

        # a default, global value for rho. 0 indicates unassigned.
        self._rho = 0.0

        # do I drop proximal (quadratic penalty) terms from the
        # weighted objective functions?
        self._drop_proximal_terms = False

        # do I retain quadratic objective terms associated with binary
        # variables? in general, there is no good reason to not
        # linearize, but just in case, we introduced the option.
        self._retain_quadratic_binary_terms = False

        # do I linearize the quadratic penalty term for continuous
        # variables via a piecewise linear approximation? the default
        # should always be 0 (off), as the user should be aware when
        # they are forcing an approximation.
        self._linearize_nonbinary_penalty_terms = 0

        # the breakpoint distribution strategy employed when
        # linearizing. 0 implies uniform distribution between the
        # variable lower and upper bounds.
        self._breakpoint_strategy = 0

        # PH default tolerances - for use in fixing and testing
        # equality across scenarios, and other stuff.
        self._integer_tolerance = 0.00001

        # when bundling, we cache the extensive form binding instances
        # to save re-generation costs.
        # maps bundle name in a scenario tree to the binding instance
        self._bundle_binding_instance_map = {}
        # maps bundle name in a scenario tree to a name->instance map
        # of the scenario instances in the bundle
        self._bundle_scenario_instance_map = {}

        # a simple boolean flag indicating whether or not this ph
        # instance has received an initialization method and has
        # successfully processed it.
        self._initialized = False

    def initialize(self, *args, **kwds):
        raise NotImplementedError("_PHBase::initialize() is an abstract method")

    #
    # Creates a deterministic symbol map for variables on an
    # instance. This allows convenient transmission of information to
    # and from PHSolverServers and makes it easy to save solutions
    # using a pickleable dictionary of symbols -> values
    #
    def _create_instance_symbol_maps(self, ctypes):

        for instance in itervalues(self._instances):

            create_block_symbol_maps(instance, ctypes)

    def solve(self, *args, **kwds):
        raise NotImplementedError("_PHBase::solve() is an abstract method")

    # restores the variable values for all of the scenario instances
    # that I maintain.  restoration proceeds from the
    # self._cached_solutions map. if this is not populated (via
    # setting cache_results=True when calling solve_subproblems), then
    # an exception will be thrown.

    def restoreCachedScenarioSolutions(self, *args, **kwds):
        raise NotImplementedError("_PHBase::restoreCachedScenarioSolutions() is "
                                  "an abstract method")

    # 
    # when bundling, form the extensive form binding instances given
    # the current scenario tree specification.  unless bundles are
    # dynamic, only needs to be invoked once, before PH iteration
    # 0. otherwise, needs to be invoked each time the bundle structure
    # is redefined.
    #
    # the resulting binding instances are stored in:
    # self._bundle_extensive_form_map.  the scenario instances
    # associated with a bundle are stored in:
    # self._bundle_scenario_instance_map.
    #
    
    def _form_bundle_binding_instances(self, preprocess_objectives=True):

        start_time = time.time()
        if self._verbose:
           print("Forming binding instances for all scenario bundles")
       
        self._bundle_binding_instance_map.clear()
        self._bundle_scenario_instance_map.clear()

        if self._scenario_tree.contains_bundles() is False:
           raise RuntimeError("Failed to create binding instances for scenario "
                              "bundles - no scenario bundles are defined!")

        for scenario_bundle in self._scenario_tree._scenario_bundles:        

            if self._verbose:
                print("Creating binding instance for scenario bundle="
                      +scenario_bundle._name)

            self._bundle_scenario_instance_map[scenario_bundle._name] = {}
            for scenario_name in scenario_bundle._scenario_names:
               self._bundle_scenario_instance_map[scenario_bundle._name]\
                   [scenario_name] = self._instances[scenario_name]

            # IMPORTANT: The bundle variable IDs must be idential to
            #            those in the parent scenario tree - this is
            #            critical for storing results, which occurs at
            #            the full-scale scenario tree.

            # WARNING: THIS IS A PURE HACK - WE REALLY NEED TO CALL
            #          THIS WHEN WE CONSTRUCT THE BUNDLE SCENARIO
            #          TREE.  AS IT STANDS, THIS MUST BE DONE BEFORE
            #          CREATING THE EF INSTANCE.

            scenario_bundle._scenario_tree.linkInInstances(
                self._instances,
                create_variable_ids=False,
                master_scenario_tree=self._scenario_tree)

            # **Note: create_ef_instance assumes the scenario
            #         instances have been preprocessed (not required)
            #         and only preprocesses the required components
            #         that have been added to the subinstances or the
            #         binding instance. So no further preprocessing is
            #         required.
            bundle_ef_instance = create_ef_instance(
                scenario_bundle._scenario_tree,
                self._bundle_scenario_instance_map[scenario_bundle._name],
                ef_instance_name = scenario_bundle._name,
                verbose_output = self._verbose)

            self._bundle_binding_instance_map[scenario_bundle._name] = \
                bundle_ef_instance

            # Adding the ph objective terms to the bundle
            bundle_ef_objective_data = \
                find_active_objective(bundle_ef_instance, safety_checks=True)

            # augment the EF objective with the PH penalty terms for
            # each composite scenario.
            for scenario_name in scenario_bundle._scenario_names:
                proximal_expression_component = \
                    self._problem_states.\
                    ph_objective_proximal_expressions[scenario_name][0]
                weight_expression_component = \
                    self._problem_states.\
                    ph_objective_weight_expressions[scenario_name][0]
                scenario = self._scenario_tree._scenario_map[scenario_name]
                bundle_ef_objective_data.expr += \
                    (scenario._probability / scenario_bundle._probability) * \
                    proximal_expression_component
                bundle_ef_objective_data.expr += \
                    (scenario._probability / scenario_bundle._probability) * \
                    weight_expression_component

            # _preprocess_scenario_instances will preprocess the
            # binding instance objective when at least one subinstance
            # objective is flagged for preprocessing. So the
            # preprocessing below is not required the way this
            # function currently used (in ph initialization, BEFORE
            # preprocessing any scenario instances).
            if preprocess_objectives is True:
                if self._solver.problem_format == ProblemFormat.nl:
                    ampl_preprocess_block_objectives(bundle_ef_instance)
                else:
                    canonical_preprocess_block_objectives(bundle_ef_instance, {})

        end_time = time.time()

        if self._output_times:
            print("Scenario bundle construction time=%.2f seconds"
                  % (end_time - start_time))

    def add_ph_objective_proximal_terms(self):

        start_time = time.time()

        for instance_name, instance in iteritems(self._instances):

            if not self._problem_states.\
                  has_ph_objective_proximal_terms[instance_name]:
                expression_component, proximal_expression = \
                    add_ph_objective_proximal_terms(instance_name,
                                                    instance,
                                                    self._scenario_tree,
                                                    self._linearize_nonbinary_penalty_terms,
                                                    self._retain_quadratic_binary_terms)

                self._problem_states.\
                    ph_objective_proximal_expressions[instance_name] = \
                        (expression_component, proximal_expression)
                self._problem_states.\
                    has_ph_objective_proximal_terms[instance_name] = True
                # Flag the preprocessor
                self._problem_states.objective_updated[instance_name] = True

        end_time = time.time()

        if self._output_times:
            print("Add PH objective proximal terms time=%.2f seconds"
                  % (end_time - start_time))

    def activate_ph_objective_proximal_terms(self, transmit=False):

        start_time = time.time()

        for instance_name, instance in iteritems(self._instances):

            if not self._problem_states.\
                  has_ph_objective_proximal_terms[instance_name]:
                expression_component, expression = \
                    self._problem_states.\
                    ph_objective_proximal_expressions[instance_name]
                expression_component.value = expression
                self._problem_states.\
                    has_ph_objective_proximal_terms[instance_name] = True
                # Flag the preprocessor
                self._problem_states.objective_updated[instance_name] = True

        if transmit is True:
            if isinstance(self._solver_manager,
                          coopr.solvers.plugins.smanager.\
                          phpyro.SolverManager_PHPyro):
                activate_ph_objective_proximal_terms(self)

        end_time = time.time()

        if self._output_times:
            print("Activate PH objective proximal terms time=%.2f seconds"
                  % (end_time - start_time))

    def deactivate_ph_objective_proximal_terms(self, transmit=False):

        start_time = time.time()

        for instance_name, instance in iteritems(self._instances):

            if self._problem_states.\
                  has_ph_objective_proximal_terms[instance_name]:
                self._problem_states.\
                    ph_objective_proximal_expressions[instance_name][0].value = 0.0
                self._problem_states.\
                    has_ph_objective_proximal_terms[instance_name] = False
                # Flag the preprocessor
                self._problem_states.objective_updated[instance_name] = True

        if transmit is True:
            if isinstance(self._solver_manager,
                          coopr.solvers.plugins.smanager.\
                          phpyro.SolverManager_PHPyro):
                deactivate_ph_objective_proximal_terms(self)

        end_time = time.time()

        if self._output_times:
            print("Deactivate PH objective proximal terms time=%.2f seconds"
                  % (end_time - start_time))

    def add_ph_objective_weight_terms(self):

        start_time = time.time()

        for instance_name, instance in iteritems(self._instances):

            if not self._problem_states.\
                  has_ph_objective_weight_terms[instance_name]:
                expression_component, expression = \
                    add_ph_objective_weight_terms(instance_name,
                                                  instance,
                                                  self._scenario_tree)

                self._problem_states.\
                    ph_objective_weight_expressions[instance_name] = \
                        (expression_component, expression)
                self._problem_states.\
                    has_ph_objective_weight_terms[instance_name] = True
                # Flag the preprocessor
                self._problem_states.objective_updated[instance_name] = True

        end_time = time.time()

        if self._output_times:
            print("Add PH objective weight terms time=%.2f seconds"
                  % (end_time - start_time))

    def activate_ph_objective_weight_terms(self, transmit=False):

        start_time = time.time()

        for instance_name, instance in iteritems(self._instances):

            if not self._problem_states.\
                  has_ph_objective_weight_terms[instance_name]:
                expression_component, expression = \
                    self._problem_states.\
                    ph_objective_weight_expressions[instance_name]
                expression_component.value = expression
                self._problem_states.\
                    has_ph_objective_weight_terms[instance_name] = True
                # Flag the preprocessor
                self._problem_states.objective_updated[instance_name] = True

        if transmit is True:
            if isinstance(self._solver_manager,
                          coopr.solvers.plugins.smanager.\
                          phpyro.SolverManager_PHPyro):
                activate_ph_objective_weight_terms(self)

        end_time = time.time()

        if self._output_times:
            print("Activate PH objective weight terms time=%.2f seconds"
                  % (end_time - start_time))

    def deactivate_ph_objective_weight_terms(self, transmit=False):

        start_time = time.time()

        for instance_name, instance in iteritems(self._instances):

            if self._problem_states.\
               has_ph_objective_weight_terms[instance_name]:
                self._problem_states.\
                    ph_objective_weight_expressions[instance_name][0].value = 0.0
                self._problem_states.\
                    has_ph_objective_weight_terms[instance_name] = False
                # Flag the preprocessor
                self._problem_states.objective_updated[instance_name] = True

        if transmit is True:
            if isinstance(self._solver_manager,
                          coopr.solvers.plugins.smanager.\
                          phpyro.SolverManager_PHPyro):
                deactivate_ph_objective_weight_terms(self)

        end_time = time.time()

        if self._output_times:
            print("Deactivate PH objective weight terms time=%.2f "
                  "seconds" % (end_time - start_time))

    def _push_w_to_instances(self):

        for scenario in self._scenario_tree._scenarios:
            scenario.push_w_to_instance()
            # The objectives are always updated when the weight params are updated
            # and weight terms exist
            if self._problem_states.has_ph_objective_weight_terms[scenario._name]:
                # Flag the preprocessor
                self._problem_states.objective_updated[scenario._name] = True

    def _push_rho_to_instances(self):

        for scenario in self._scenario_tree._scenarios:
            scenario.push_rho_to_instance()
            # The objectives are always updated when the rho params are updated
            # and the proximal terms exist
            if self._problem_states.has_ph_objective_proximal_terms[scenario._name]:
                # Flag the preprocessor
                self._problem_states.objective_updated[scenario._name] = True

    def _push_xbar_to_instances(self):

        for stage in self._scenario_tree._stages[:-1]:
            for tree_node in stage._tree_nodes:
                tree_node.push_xbar_to_instances()
        for scenario in self._scenario_tree._scenarios:
            # The objectives are always updated when the xbar params are updated
            # and proximal terms exist
            if self._problem_states.has_ph_objective_proximal_terms[scenario._name]:
                # Flag the preprocessor
                self._problem_states.objective_updated[scenario._name] = True

    def _push_fixed_to_instances(self):

        for tree_node in self._scenario_tree._tree_nodes:

            if len(tree_node._fix_queue):

                """
                some_fixed = tree_node.has_fixed_in_queue()
                some_freed = tree_node.has_freed_in_queue()
                # flag the preprocessor
                if some_fixed or some_freed:
                    for scenario in tree_node._scenarios:
                        scenario_name = scenario._name
                        self._problem_states.\
                            fixed_variables[scenario_name] |= some_fixed
                        self._problem_states.\
                            freed_variables[scenario_name] |= some_freed
                """
                for scenario in tree_node._scenarios:
                    scenario_name = scenario._name
                    for variable_id, (fixed_status, new_value) in \
                          iteritems(tree_node._fix_queue):
                        variable_name, index = tree_node._variable_ids[variable_id]
                        if fixed_status == tree_node.VARIABLE_FREED:
                            self._problem_states.\
                                freed_variables[scenario_name].\
                                append((variable_name, index))
                        elif fixed_status == tree_node.VARIABLE_FIXED:
                            self._problem_states.\
                                fixed_variables[scenario_name].\
                                append((variable_name, index))
                tree_node.push_fixed_to_instances()

    #
    # when linearizing the PH objective, PHQUADPENALTY* variables are
    # introduced. however, the inclusion / presence of these variables
    # in warm-start files leads to infeasible MIP starts. thus, we
    # want to flag their value as None in all scenario instances prior
    # to performing scenario sub-problem solves.
    #

    def _reset_instance_linearization_variables(self):

       for scenario_name, scenario_instance in iteritems(self._instances):
           if self._problem_states.has_ph_variables(scenario_name):
               reset_linearization_variables(scenario_instance)

    def form_ph_linearized_objective_constraints(self):

        start_time = time.time()

        for instance_name, instance in iteritems(self._instances):

            if self._problem_states.has_ph_objective_proximal_terms[instance_name]:
                new_attrs = form_linearized_objective_constraints(
                    instance_name,
                    instance,
                    self._scenario_tree,
                    self._linearize_nonbinary_penalty_terms,
                    self._breakpoint_strategy,
                    self._integer_tolerance)

                self._problem_states.ph_constraints[instance_name].extend(new_attrs)
                self._problem_states.ph_constraints_updated[instance_name] = True

        end_time = time.time()

        if self._output_times:
            print("PH linearized objective constraint formation "
                  "time=%.2f seconds" % (end_time - start_time))

    # 
    # a utility to perform preprocessing on all scenario instances, on
    # an as-needed basis.  queries the instance modification indicator
    # attributes on the ProgressiveHedging (self) object. intended to
    # be invoked before each iteration of PH, just before scenario
    # solves.
    #

    def _preprocess_scenario_instances(self):

        start_time = time.time()

        if self._scenario_tree.contains_bundles():
            
            for scenario_bundle_name, bundle_ef_instance in iteritems(
                    self._bundle_binding_instance_map):

                # Until proven otherwise
                preprocess_bundle_objective = False
                preprocess_bundle_constraints = False

                for scenario_name in \
                      self._bundle_scenario_instance_map[scenario_bundle_name]:

                    scenario_instance = self._instances[scenario_name]
                    fixed_vars = self._problem_states.fixed_variables[scenario_name]
                    freed_vars = self._problem_states.freed_variables[scenario_name]
                    objective_updated = \
                        self._problem_states.objective_updated[scenario_name]

                    if objective_updated:
                        preprocess_bundle_objective = True
                    # TODO
                    """
                    if (fixed_vars or freed_vars) and \
                       (not self._write_fixed_variables):
                    """
                    if (len(fixed_vars) > 0 or len(freed_vars) > 0) and \
                       (not self._write_fixed_variables):
                        preprocess_bundle_objective = True
                        preprocess_bundle_constraints = True

                    preprocess_scenario_instance(
                        scenario_instance,
                        fixed_vars,
                        freed_vars,
                        self._problem_states.\
                            user_constraints_updated[scenario_name],
                        self._problem_states.ph_constraints_updated[scenario_name],
                        self._problem_states.ph_constraints[scenario_name],
                        objective_updated,
                        not self._write_fixed_variables,
                        self._solver)

                    # We've preprocessed the instance, reset the relevant flags
                    self._problem_states.clear_update_flags(scenario_name)
                    self._problem_states.clear_fixed_variables(scenario_name)
                    self._problem_states.clear_freed_variables(scenario_name)

                if self._solver.problem_format == ProblemFormat.nl:
                    if preprocess_bundle_objective:
                        ampl_preprocess_block_objectives(bundle_ef_instance)
                    if preprocess_bundle_constraints:
                        ampl_preprocess_block_constraints(bundle_ef_instance)
                else:
                    var_id_map = {}
                    if preprocess_bundle_objective:
                        canonical_preprocess_block_objectives(bundle_ef_instance,
                                                              var_id_map)
                    if preprocess_bundle_constraints:
                        canonical_preprocess_block_constraints(bundle_ef_instance,
                                                               var_id_map)
        else:

            for scenario_name, scenario_instance in iteritems(self._instances):

                preprocess_scenario_instance(
                    scenario_instance,
                    self._problem_states.fixed_variables[scenario_name],
                    self._problem_states.freed_variables[scenario_name],
                    self._problem_states.user_constraints_updated[scenario_name],
                    self._problem_states.ph_constraints_updated[scenario_name],
                    self._problem_states.ph_constraints[scenario_name],
                    self._problem_states.objective_updated[scenario_name],
                    not self._write_fixed_variables,
                    self._solver)

                # We've preprocessed the instance, reset the relevant flags
                self._problem_states.clear_update_flags(scenario_name)
                self._problem_states.clear_fixed_variables(scenario_name)
                self._problem_states.clear_freed_variables(scenario_name)

        end_time = time.time()

        if self._output_times:
            print("Scenario instance preprocessing time=%.2f seconds"
                  % (end_time - start_time))

    #
    # create PH weight and xbar vectors, on a per-scenario basis, for
    # each variable that is not in the final stage, i.e., for all
    # variables that are being blended by PH. the parameters are
    # created in the space of each scenario instance, so that they can
    # be directly and automatically incorporated into the
    # (appropriately modified) objective function.
    #

    def _create_scenario_ph_parameters(self):

        create_nodal_ph_parameters(self._scenario_tree)

        for instance_name, instance in iteritems(self._instances):
            new_penalty_variable_names = create_ph_parameters(
                instance,
                self._scenario_tree,
                self._rho,
                self._linearize_nonbinary_penalty_terms)

            if new_penalty_variable_names != []:
                self._problem_states.ph_variables[instance_name].\
                    extend(new_penalty_variable_names)

    #
    # a pair of utilities intended for folks who are brave enough to
    # script rho setting in a python file.
    #

    # NOTE: rho_expression can be Pyomo expression, or a constant
    #       float/int. either way, the underlying value will be
    #       extracted via a value() call...
    def setRhoAllScenarios(self, tree_node, variable_id, rho_expression):

        new_rho_value = value(rho_expression)

        for scenario in tree_node._scenarios:

            scenario._rho[tree_node._name][variable_id] = new_rho_value

    def setRhoOneScenario(self, tree_node, scenario, variable_id, rho_expression):

        scenario._rho[tree_node._name][variable_id] = value(rho_expression)

    def getRhoOneScenario(self, tree_node, scenario, variable_id):

        return scenario._rho[tree_node._name][variable_id]

    #
    # a utility intended for folks who are brave enough to script
    # variable bounds setting in a python file.
    #    
    def setVariableBoundsAllScenarios(self,
                                      tree_node,
                                      variable_id,
                                      lower_bound,
                                      upper_bound):

        for scenario in tree_node._scenarios:
            vardata = scenario._instance.\
                      _ScenarioTreeSymbolMap.getObject(variable_id)
            vardata.setlb(lower_bound)
            vardata.setub(upper_bound)

    def setVariableBoundsOneScenario(self,
                                     tree_node,
                                     scenario,
                                     variable_id,
                                     lower_bound,
                                     upper_bound):

        vardata = scenario._instance._ScenarioTreeSymbolMap.getObject(variable_id)
        vardata.setlb(lower_bound)
        vardata.setub(upper_bound)

    #
    # a utility intended for folks who are brave enough to script
    # variable bounds setting in a python file.  same functionality as
    # above, but applied to all indicies of the variable, in all
    # scenarios.
    #
    """
    def setVariableBoundsAllIndicesAllScenarios(self, variable_name, lower_bound, upper_bound):

        if isinstance(lower_bound, float) is False:
            raise ValueError("Lower bound supplied to PH method setVariableBoundsAllIndiciesAllScenarios for variable="+variable_name+" must be a constant; value supplied="+str(lower_bound))

        if isinstance(upper_bound, float) is False:
            raise ValueError("Upper bound supplied to PH method setVariableBoundsAllIndicesAllScenarios for variable="+variable_name+" must be a constant; value supplied="+str(upper_bound))

        for instance_name, instance in iteritems(self._instances):

            variable = instance.find_component(variable_name)
            for index in variable:
                variable[index].setlb(lower_bound)
                variable[index].setub(upper_bound)
    """

class ProgressiveHedging(_PHBase):
    
    def __del__(self):

        #print "Called __del__ on ProgressiveHedging plugin; garbage collecting?"
        #print hpy().heap()

        # both the solver and solver managers are plugins, which means that they 
        # need to be deactivated in order for their memory to be released. not
        # a big deal if running from a command-line script, but definitely a 
        # big deal when execting PH in a scripting context.

        # WEH - This may not be necessary after the move to the new
        #   Coopr plugins.
        if self._solver != None:
            self._solver.deactivate()

        if self._solver_manager != None:
            self._solver_manager.deactivate()
        
    #
    # checkpoint the current PH state via pickle'ing. the input iteration count
    # simply serves as a tag to create the output file name. everything with the
    # exception of the _ph_plugins, _solver_manager, and _solver attributes are
    # pickled. currently, plugins fail in the pickle process, which is fine as
    # JPW doesn't think you want to pickle plugins (particularly the solver and
    # solver manager) anyway. For example, you might want to change those later,
    # after restoration - and the PH state is independent of how scenario
    # sub-problems are solved.
    #

    def checkpoint(self, iteration_count):

        checkpoint_filename = "checkpoint."+str(iteration_count)

        tmp_ph_plugins = self._ph_plugins
        tmp_solver_manager = self._solver_manager
        tmp_solver = self._solver

        self._ph_plugins = None
        self._solver_manager = None
        self._solver = None

        checkpoint_file = open(checkpoint_filename, "w")
        pickle.dump(self,checkpoint_file)
        checkpoint_file.close()

        self._ph_plugins = tmp_ph_plugins
        self._solver_manager = tmp_solver_manager
        self._solver = tmp_solver

        print("Checkpoint written to file="+checkpoint_filename)

    def _push_w_to_instances(self):

        if isinstance(self._solver_manager,
                      coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):
            transmit_weights(self)
        else:
            _PHBase._push_w_to_instances(self)

    def _push_rho_to_instances(self):

        if isinstance(self._solver_manager,
                      coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):
            # NOTE: It is likely we no longer need this function
            transmit_rhos(self)
        else:
            _PHBase._push_rho_to_instances(self)

    def _push_xbar_to_instances(self):

        if isinstance(self._solver_manager,
                      coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):
            transmit_xbars(self)
        else:
            _PHBase._push_xbar_to_instances(self)

    def _push_fixed_to_instances(self):

        if isinstance(self._solver_manager,
                      coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):
            transmit_fixed_variables(self)
            for tree_node in self._scenario_tree._tree_nodes:
                # Note: If the scenario tree doesn't not have
                #       instances linked in this method will simply
                #       empty the queue into the tree node fixed list
                #       without trying to fix instance variables
                tree_node.push_fixed_to_instances()
        else:
            _PHBase._push_fixed_to_instances(self)

    #
    # restores the current solutions of all scenario instances that I maintain.
    # Additionally, if running with PHPyro, asks solver servers to do the same.
    # 

    def restoreCachedScenarioSolutions(self):

        if len(self._cached_solutions) is 0:
            raise RuntimeError("Cannot restore scenario solutions - the cached scenario solution map is empty!")

        if isinstance(self._solver_manager, coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):
            restore_cached_scenario_solutions(self)

        if self._scenario_tree.contains_bundles() is True:
            if isinstance(self._solver_manager, coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):
                for scenario_name, scenario_results in iteritems(self._cached_solutions):
                    scenario = self._scenario_tree.get_scenario(scenario_name)
                    scenario.update_current_solution(scenario_results)
            else:
                for bundle_name, (results, fixed_results_dict) in iteritems(self._cached_solutions):
                    self._bundle_binding_instance_map[bundle_name].load(results,
                                                                        allow_consistent_values_for_fixed_vars=self._write_fixed_variables,
                                                                        comparison_tolerance_for_fixed_vars=self._comparison_tolerance_for_fixed_vars)
                    for scenario_name, fixed_results in iteritems(fixed_results_dict):
                        scenario_instance = self._instances[scenario_name]
                        bySymbol = scenario_instance._PHInstanceSymbolMaps[Var].bySymbol
                        for instance_id, varvalue, stale_flag in fixed_results:
                            vardata = bySymbol[instance_id]
                            vardata.value = varvalue
                            vardata.fixed = True
                            vardata.stale = stale_flag
        else:
            if isinstance(self._solver_manager, coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):
                for scenario_name, scenario_results in iteritems(self._cached_solutions):
                    scenario = self._scenario_tree.get_scenario(scenario_name)
                    scenario.update_current_solution(scenario_results)
            else:
                for scenario_name, (results, fixed_results) in iteritems(self._cached_solutions):
                    scenario_instance = self._instances[scenario_name]
                    scenario_instance.load(results,
                                           allow_consistent_values_for_fixed_vars=self._write_fixed_variables,
                                           comparison_tolerance_for_fixed_vars=self._comparison_tolerance_for_fixed_vars)
                    bySymbol = scenario_instance._PHInstanceSymbolMaps[Var].bySymbol
                    for instance_id, varvalue, stale_flag in fixed_results:
                        vardata = bySymbol[instance_id]
                        vardata.value = varvalue
                        vardata.fixed = True
                        vardata.stale = stale_flag

    #
    # a simple utility to count the number of continuous and discrete
    # variables in a set of instances.  this is based on the number of
    # active, non-stale variables in the instances. returns a pair -
    # num-discrete, num-continuous.  IMPT: This should obviously only
    # be called *after* the scenario instances have been solved -
    # otherwise, everything is stale - and you'll get back (0,0).
    #
    # This method is assumed to be called ONCE immediately following
    # the iteration 0 solves. Otherwise, the fixing/freeing of
    # variables may interact with the stale flag in different and
    # unexpected ways depending on what option we choose for treating
    # fixed variable preprocessing.
    #

    def compute_blended_variable_counts(self):

        assert self._called_compute_blended_variable_counts is False
        self._called_compute_blended_variable_counts = True

        num_continuous_vars = 0
        num_discrete_vars = 0

        for stage, tree_node, variable_id, var_values, is_fixed, is_stale \
              in scenario_tree_node_variables_generator_noinstances(
                  self._scenario_tree,
                  includeDerivedVariables=False,
                  includeLastStage=False):

            if not is_stale:
                if tree_node.is_variable_discrete(variable_id):
                    num_discrete_vars = num_discrete_vars + 1
                else:
                    num_continuous_vars = num_continuous_vars + 1

        return (num_discrete_vars, num_continuous_vars)

    #
    # ditto above, but count the number of fixed discrete and
    # continuous variables.
    #

    def compute_fixed_variable_counts(self):

        num_fixed_continuous_vars = 0
        num_fixed_discrete_vars = 0

        for stage, tree_node, variable_id, var_values, is_fixed, is_stale \
              in scenario_tree_node_variables_generator_noinstances(
                  self._scenario_tree,
                  includeDerivedVariables=False,
                  includeLastStage=False):

            if is_fixed:
                if tree_node.is_variable_discrete(variable_id):
                    num_fixed_discrete_vars = num_fixed_discrete_vars + 1
                else:
                    num_fixed_continuous_vars = num_fixed_continuous_vars + 1

        return (num_fixed_discrete_vars, num_fixed_continuous_vars)

    #
    # when the quadratic penalty terms are approximated via piecewise
    # linear segments, we end up (necessarily) "littering" the
    # scenario instances with extra constraints.  these need to and
    # should be cleaned up after PH, for purposes of post-PH
    # manipulation, e.g., writing the extensive form. equally
    # importantly, we need to re-establish the original instance
    # objectives.
    #

    def _cleanup_scenario_instances(self):

        for instance_name, instance in iteritems(self._instances):

            # Eliminate references to ph constraints
            for constraint_name in self._problem_states.ph_constraints[instance_name]:
                instance.del_component(constraint_name)
            self._problem_states.clear_ph_constraints(instance_name)
            
            # Eliminate references to ph variables
            for variable_name in self._problem_states.ph_variables[instance_name]:
                instance.del_component(variable_name)
            self._problem_states.clear_ph_variables(instance_name)

            #del instance._ScenarioTreeSymbolMap
            del instance._PHInstanceSymbolMaps

        # Activate the original objective form
        # Don't bother transmitting these deactivation signals to the 
        # ph solver servers as this function is being called at the end of ph (for now)
        self.deactivate_ph_objective_weight_terms(transmit=False)
        if self._drop_proximal_terms is False:
            self.deactivate_ph_objective_proximal_terms(transmit=False)

        

    #
    # a simple utility to extract the first-stage cost statistics, e.g., min, average, and max.
    #

    def _extract_first_stage_cost_statistics(self):

        maximum_value = 0.0
        minimum_value = 0.0
        sum_values = 0.0
        num_values = 0
        first_time = True

        root_node = self._scenario_tree.findRootNode()
        first_stage_name = root_node._stage._name
        for scenario in root_node._scenarios:
            this_value = scenario._stage_costs[first_stage_name]
            # None means not reported by the solver.
            if this_value is not None:
                num_values += 1
                sum_values += this_value
                if first_time:
                    first_time = False
                    maximum_value = this_value
                    minimum_value = this_value
                else:
                    if this_value > maximum_value:
                        maximum_value = this_value
                    if this_value < minimum_value:
                        minimum_value = this_value

        if num_values > 0:
            sum_values = sum_values / num_values

        return minimum_value, sum_values, maximum_value

    def __init__(self, options, dual_ph=False):

        _PHBase.__init__(self)

        # Make sure we don't call a method more than once
        self._called_compute_blended_variable_counts = False

        # Augment the code where necessary to run the dual ph algorithm
        self._dual_ph = dual_ph

        # Do we cache the most recent set of scenario/bundle solutions.
        # Default is no, because there is no use for it. However,
        # this can be a very useful flag to activate for certain
        # phextensions that do things like resolve scenarios/bundles
        # (e.g., phboundextenion, convexhullboundextension) when they
        # want to avoid affecting ph convergence due to warmstarting
        # issues.
        self._enable_solution_caching = False

        # Define the default configuration for what variable
        # values to include inside interation k phsolverserver
        # results. See phsolverserverutils for more information.
        # The default case sends the minimal set of information
        # needed to update ph objective parameters, which would
        # be nonleaf node ph variables that are not stale.
        # Plugins like phhistoryextension modify this flag to
        # include more information (e.g., leaf stage values)
        # ** NOTE **: If we do not preprocess fixed variables (default behavior),
        #             stale=True is equivalent to extraneous variables declared
        #             on the model and scenario tree that are never used (fixed or not).
        #             When we do preprocess fixed variables, the stale=True applies
        #             to the above case as well as fixed variables (which become stale).
        #             ...just something to keep in mind
        self._phpyro_default_iteration_k_variable_transmission = \
            TransmitType.nonleaf_stages | \
            TransmitType.blended | \
            TransmitType.derived

        self._overrelax = False 
        # a default, global value for nu. 0 indicates unassigned.
        self._nu = 0.0
        # filename for the modeler to set rho on a per-variable or
        # per-scenario basis.
        self._rho_setter = None
        # filename for the modeler to collect aggregate scenario data
        self._aggregate_getter = None
        # filename for the modeler to set rho on a per-variable basis,
        # after all scenarios are available.
        self._bound_setter = None
        self._max_iterations = 0
        self._async = False
        self._async_buffer_len = 1

        # it may be the case that some plugins think they can do a better job of weight updates
        # than PH - and it might even be true! if so, set this flag to False and this class
        # will not invoke the update_weights() method.
        self._ph_weight_updates_enabled = True

        # PH reporting parameters
        #self._verbose = False # do I flood the screen with status output?
        self._report_solutions = False # do I report solutions after each PH iteration?
        self._report_weights = False # do I report PH weights prior to each PH iteration?
        self._report_only_statistics = False # do I report only variable statistics when outputting solutions and weights?
        self._report_for_zero_variable_values = False # do I report statistics (via pprint()) for all variables, including those whose values equal 0?
        self._report_only_nonconverged_variables = False # do I report statistics (via pprint()) for only non-converged variables?
        self._output_continuous_variable_stats = True # when in verbose mode, do I output weights/averages for continuous variables?
        self._output_solver_results = False
        self._output_scenario_tree_solution = False

        # PH performance diagnostic parameters and related timing parameters.
        self._profile_memory = 0 # indicates disabled.
        self._time_since_last_garbage_collect = time.time()
        self._minimum_garbage_collection_interval = 5 # units are seconds

        # PH run-time variables
        self._current_iteration = 0 # the 'k'

        self._solver_manager_type = "serial" # serial, pyro, and phpyro are the options currently available

        # options for writing solver files / logging / etc.
        self._keep_solver_files = False
        self._symbolic_solver_labels = False
        self._output_solver_logs = False

        # string to support suffix specification by callbacks
        self._extensions_suffix_list = None

        # PH convergence computer/updater.
        self._converger = None

        # the checkpoint interval - expensive operation, but worth it for big models.
        # 0 indicates don't checkpoint.
        self._checkpoint_interval = 0

        # the source model and instance directories.
        self._model_directory_name = ""
        self._instance_directory_name = ""

        # global handle to ph extension plugins
        self._ph_plugins = ExtensionPoint(IPHExtension)

        # PH timing statistics - relative to last invocation.
        self._init_start_time = None # for initialization() method
        self._init_end_time = None
        self._solve_start_time = None # for solve() method
        self._solve_end_time = None
        self._cumulative_solve_time = None # seconds, over course of solve()
        self._cumulative_xbar_time = None # seconds, over course of update_xbars()
        self._cumulative_weight_time = None # seconds, over course of update_weights()

        # do I disable warm-start for scenario sub-problem solves
        # during PH iterations >= 1?
        self._disable_warmstarts = False

        # PH maintains a mipgap that is applied to each scenario solve
        # that is performed.  this attribute can be changed by PH
        # extensions, and the change will be applied on all subsequent
        # solves - until it is modified again. the default is None,
        # indicating unassigned.
        self._mipgap = None

        # we only store these temporarily...
        scenario_solver_options = None

        # process the keyword options
        self._max_iterations                      = options.max_iterations
        self._overrelax                           = options.overrelax
        self._nu                                  = options.nu
        self._async                               = options.async
        self._async_buffer_len                    = options.async_buffer_len
        self._rho                                 = options.default_rho
        self._rho_setter                          = options.rho_cfgfile
        self._aggregate_getter                    = options.aggregate_cfgfile
        self._bound_setter                        = options.bounds_cfgfile
        self._solver_type                         = options.solver_type
        self._solver_io                           = options.solver_io
        self._solver_manager_type                 = options.solver_manager_type
        scenario_solver_options                   = options.scenario_solver_options
        self._handshake_with_phpyro               = options.handshake_with_phpyro
        self._mipgap                              = options.scenario_mipgap
        self._write_fixed_variables               = options.write_fixed_variables
        self._keep_solver_files                   = options.keep_solver_files
        self._symbolic_solver_labels              = options.symbolic_solver_labels
        self._output_solver_results               = options.output_solver_results
        self._output_solver_logs                  = options.output_solver_logs
        self._verbose                             = options.verbose
        self._report_solutions                    = options.report_solutions
        self._report_weights                      = options.report_weights
        self._report_only_statistics              = options.report_only_statistics
        self._report_for_zero_variable_values     = options.report_for_zero_variable_values
        self._report_only_nonconverged_variables  = options.report_only_nonconverged_variables
        self._output_times                        = options.output_times
        self._output_instance_construction_times  = options.output_instance_construction_times
        self._disable_warmstarts                  = options.disable_warmstarts
        self._drop_proximal_terms                 = options.drop_proximal_terms
        self._retain_quadratic_binary_terms       = options.retain_quadratic_binary_terms
        self._linearize_nonbinary_penalty_terms   = options.linearize_nonbinary_penalty_terms
        self._breakpoint_strategy                 = options.breakpoint_strategy
        self._checkpoint_interval                 = options.checkpoint_interval
        self._output_scenario_tree_solution       = options.output_scenario_tree_solution
        self._objective_sense = options.objective_sense
        if hasattr(options, "profile_memory"):
            self._profile_memory = options.profile_memory
        else:
            self._profile_memory = False

        if self._drop_proximal_terms is True:
            raise NotImplementedError("The option '--drop-proximal-terms' has not been fully implemented within runph.")
        
        # cache stuff relating to scenario tree manipulation - the ph solver servers may need it.
        self._scenario_bundle_specification = options.scenario_bundle_specification
        self._create_random_bundles = options.create_random_bundles
        self._scenario_tree_random_seed = options.scenario_tree_random_seed
        
        # hack by DLW 20 June 20112
        for plugin in self._ph_plugins:
            plugin._options = options

        # validate all "atomic" options (those that can be validated independently)
        if self._max_iterations < 0:
            raise ValueError("Maximum number of PH iterations must be non-negative; value specified=" + str(self._max_iterations))
        if self._rho <= 0.0:
            raise ValueError("Value of the rho parameter in PH must be non-zero positive; value specified=" + str(self._rho))
        if self._nu <= 0.0 or self._nu >= 2:
            raise ValueError("Value of the nu parameter in PH must be on the interval (0, 2); value specified=" + str(self._nu))
        if (self._mipgap is not None) and ((self._mipgap < 0.0) or (self._mipgap > 1.0)):
            raise ValueError("Value of the mipgap parameter in PH must be on the unit interval; value specified=" + str(self._mipgap))

        # validate the linearization (number of pieces) and breakpoint distribution parameters.
        if self._linearize_nonbinary_penalty_terms < 0:
            raise ValueError("Value of linearization parameter for nonbinary penalty terms must be non-negative; value specified=" + str(self._linearize_nonbinary_penalty_terms))
        if self._breakpoint_strategy < 0:
            raise ValueError("Value of the breakpoint distribution strategy parameter must be non-negative; value specified=" + str(self._breakpoint_strategy))
        if self._breakpoint_strategy > 3:
            raise ValueError("Unknown breakpoint distribution strategy specified - valid values are between 0 and 2, inclusive; value specified=" + str(self._breakpoint_strategy))

        # validate that callback functions exist in specified modules
        self._callback_function = {}
        for module_name, callback_name in ((self._aggregate_getter,"ph_aggregategetter_callback"),
                                           (self._rho_setter,"ph_rhosetter_callback"),
                                           (self._bound_setter,"ph_boundsetter_callback")):
            if module_name is not None:
                module = load_external_module(module_name)
                callback = None
                for oname, obj in inspect.getmembers(module):
                    if oname == callback_name:
                        callback = obj
                        break
                if callback is None:
                    raise ImportError("PH callback with name '%s' could not be found in module file: "
                                      "%s" % (callback_name, module_name))
                self._callback_function[module_name] = callback

        # validate the checkpoint interval.
        if self._checkpoint_interval < 0:
            raise ValueError("A negative checkpoint interval with value="
                             +str(self._checkpoint_interval)+" was "
                             "specified in call to PH constructor")

        # construct the sub-problem solver.
        if self._verbose:
            print("Constructing solver type="+self._solver_type)
        self._solver = SolverFactory(self._solver_type, solver_io=self._solver_io)
        if self._solver == None:
            raise ValueError("Unknown solver type=" + self._solver_type + " specified in call to PH constructor")
        if self._keep_solver_files:
            self._solver.keepfiles = True
        self._solver.symbolic_solver_labels = self._symbolic_solver_labels
        if len(scenario_solver_options) > 0:
            if self._verbose:
                print("Initializing scenario sub-problem solver with options="+str(scenario_solver_options))
            self._solver.set_options("".join(scenario_solver_options))
        if self._output_times:
            self._solver._report_timing = True

        # construct the solver manager.
        if self._verbose:
            print("Constructing solver manager of type="+self._solver_manager_type)
        self._solver_manager = SolverManagerFactory(self._solver_manager_type)
        if self._solver_manager is None:
            raise ValueError("Failed to create solver manager of type="+self._solver_manager_type+" specified in call to PH constructor")

        # a set of all valid PH iteration indicies is generally useful for plug-ins, so create it here.
        self._iteration_index_set = Set(name="PHIterations")
        for i in range(0,self._max_iterations + 1):
            self._iteration_index_set.add(i)

        # set of constraints to retain in situations where the PH solver server manager is being used.
        # normally, we could cull all constraints (to minimize memory usage). however, there are some
        # rare situations in which we would like to retain specific constraints, to which suffix
        # information (e.g., duals) can be attached. and you need the constraint objects to use suffixes!
        # this is a set of constraint names (parent-level - we don't do this per-index).
        self._constraints_to_retain = set()

        # spit out parameterization if verbosity is enabled
        if self._verbose:
            print("PH solver configuration: ")
            print("   Max iterations="+str(self._max_iterations))
            print("   Async mode=" + str(self._async))
            print("   Async buffer len=" + str(self._async_buffer_len))
            print("   Default global rho=" + str(self._rho))
            print("   Over-relaxation enabled="+str(self._overrelax))
            if self._overrelax:
                print("   Nu=" + self._nu)
            if self._aggregate_getter is not None:
                print("   Aggregate getter callback file=" + self._aggregate_getter)
            if self._rho_setter is not None:
                print("   Rho setter callback file=" + self._rho_setter)
            if self._bound_setter is not None:
                print("   Bound setter callback file=" + self._bound_setter)
            print("   Sub-problem solver type='%s'" % str(self._solver_type))
            print("   Solver manager type='%s'" % str(self._solver_manager_type))
            print("   Keep solver files? " + str(self._keep_solver_files))
            print("   Output solver results? " + str(self._output_solver_results))
            print("   Output solver log? " + str(self._output_solver_logs))
            print("   Output times? " + str(self._output_times))
            print("   Checkpoint interval="+str(self._checkpoint_interval))

    """ Initialize PH with model and scenario data, in preparation for solve().
        Constructs and reads instances.
    """
    def initialize(self, 
                   model_directory_name=".",
                   instance_directory_name=".",
                   model=None, 
                   scenario_tree=None, 
                   converger=None, 
                   linearize=False, 
                   retain_constraints=False):

        self._init_start_time = time.time()

        print("Initializing PH")
        print("")

        # The first step in PH initialization is to impose an order on
        # the user-defined plugins. Invoking wwextensions and
        # phhistoryextensions last ensures that any any changes the
        # former makes in order to affect algorithm convergence will
        # not be seen by any other plugins until the next iteration
        # and so that the latter can properly snapshot any changes
        # made by other plugins. All remaining extensions are invoked
        # prior to these in random order. The reason is that we're
        # being lazy - ideally, this would be the user defined order
        # on the command-line.
        wwextensions = \
            [plugin for plugin in self._ph_plugins \
             if isinstance(plugin,
                           coopr.pysp.plugins.wwphextension.wwphextension)]
        phhistoryextensions = \
            [plugin for plugin in self._ph_plugins \
             if isinstance(plugin,
                           coopr.pysp.plugins.phhistoryextension.\
                           phhistoryextension)]
        ph_plugins = []
        for plugin in self._ph_plugins:
            if not (isinstance(plugin,
                               coopr.pysp.plugins.wwphextension.wwphextension) or \
                    isinstance(plugin,
                               coopr.pysp.plugins.phhistoryextension.\
                               phhistoryextension)):
                ph_plugins.append(plugin)
        ph_plugins.extend(wwextensions)
        ph_plugins.extend(phhistoryextensions)
        self._ph_plugins = ph_plugins

        # let plugins know if they care.
        if self._verbose:
            print("Invoking pre-initialization PH plugins")
        for plugin in self._ph_plugins:
            plugin.pre_ph_initialization(self)

        if not path.exists(instance_directory_name):
            raise ValueError("Scenario data directory=%s either does "
                             "not exist or cannot be read"
                             % (instance_directory_name))

        if self._verbose:
            print("Scenario data directory=" + instance_directory_name)

        self._model_directory_name = model_directory_name
        self._instance_directory_name = instance_directory_name

        if model is None:
            raise ValueError("A model must be supplied to the PH "
                             "initialize() method")

        if scenario_tree is None:
            raise ValueError("A scenario tree must be supplied to the "
                             "PH initialize() method")

        if converger is None:
            raise ValueError("A convergence computer must be supplied to "
                             "the PH initialize() method")

        # clone the input model, because we make modifications to it
        # (such as culling constraints in some cases) - we should
        # preserve it for other extra-PH purposes.
        self._model = model.clone()
        self._scenario_tree = scenario_tree
        self._converger = converger

        self._converger.reset()

        isPHPyro =  isinstance(self._solver_manager,
                               coopr.solvers.plugins.\
                               smanager.phpyro.SolverManager_PHPyro)

        initialization_action_handles = []
        if isPHPyro:

            if self._verbose:
                print("Broadcasting requests to initialize PH solver servers")

            initialization_action_handles.extend(initialize_ph_solver_servers(self))

            if self._verbose:
                print("PH solver server initialization requests successfully transmitted")

        else:
            # construct the instances for each scenario.

            # garbage collection noticeably slows down PH when dealing with
            # large numbers of scenarios. disable prior to instance construction,
            # and then re-enable. there isn't much collection to do as instances
            # are constructed.

            scenario_instance_construct_start_time = time.time()

            re_enable_gc = gc.isenabled()
            gc.disable()

            if self._verbose:
                if self._scenario_tree._scenario_based_data == 1:
                    print("Scenario-based instance initialization enabled")
                else:
                    print("Node-based instance initialization enabled")

            # the instances have been preprocessed at this point. any
            # subsequent modification(s) will trigger subsequent
            # preprocessing prior to solves.
            self._problem_states = \
                ProblemStates([scen._name for scen in \
                               self._scenario_tree._scenarios])

            ################################################
            # start of scenario instance construction loop #
            ################################################
            for scenario in self._scenario_tree._scenarios:

                scenario_instance = construct_scenario_instance(
                    self._scenario_tree,
                self._instance_directory_name,
                    scenario._name,
                    self._model,
                    self._verbose,
                    preprocess=False,
                    linearize=linearize,
                    report_timing=self._output_instance_construction_times)

                self._problem_states.objective_updated[scenario._name] = True
                self._problem_states.user_constraints_updated[scenario._name] = True

                # IMPT: disable canonical representation construction
                #       for ASL solvers.  this is a hack, in that we
                #       need to address encodings and the like at a
                #       more general level.
                if self._solver.problem_format() == ProblemFormat.nl:
                    scenario_instance.skip_canonical_repn = True
                    # We will take care of these manually within
                    # _preprocess_scenario_instance This will also
                    # prevent regenerating the ampl_repn when forming
                    # the bundle_ef's
                    scenario_instance.gen_obj_ampl_repn = False
                    scenario_instance.gen_con_ampl_repn = False

                self._instances[scenario._name] = scenario_instance
                self._instances[scenario._name].name = scenario._name

                ##############################################
                # end of scenario instance construction loop #
                ##############################################

            # perform a single pass of garbage collection and
            # re-enable automatic collection.
            if re_enable_gc:
                if (time.time() - self._time_since_last_garbage_collect) >= \
                      self._minimum_garbage_collection_interval:
                    gc.collect()
                    self._time_since_last_garbage_collect = time.time()
                gc.enable()

            scenario_instance_construct_end_time = time.time()
            if self._output_times:
                print("PH scenario instance construction time=%.2f seconds"
                      % (scenario_instance_construct_end_time - \
                         scenario_instance_construct_start_time))

            # with the scenario instances now available, link the
            # referenced objects directly into the scenario tree.
            instance_linking_start_time = time.time()
            self._scenario_tree.linkInInstances(self._instances,
                                                self._objective_sense,
                                                create_variable_ids=True)
            instance_linking_end_time = time.time()
            if self._output_times:
                print("Scenario tree instance linking time=%.2f seconds"
                      % (instance_linking_end_time - instance_linking_start_time))

        # let plugins know if they care - this callback point allows
        # users to create/modify the original scenario instances
        # and/or the scenario tree prior to creating PH-related
        # parameters, variables, and the like.
        post_instance_plugin_callback_start_time = time.time()
        for plugin in self._ph_plugins:
            plugin.post_instance_creation(self)
        post_instance_plugin_callback_end_time = time.time()
        if self._output_times:
            print("PH post-instance plugin callback time=%.2f seconds"
                  % (post_instance_plugin_callback_end_time - \
                     post_instance_plugin_callback_start_time))

        if not isPHPyro:

            # create ph-specific parameters (weights, xbar, etc.) for
            # each instance.
            if self._verbose:
                print("Creating weight, average, and rho parameter "
                      "vectors for scenario instances")
            scenario_ph_parameters_start_time = time.time()
            self._create_scenario_ph_parameters()
            scenario_ph_parameters_end_time = time.time()
            if self._output_times:
                print("PH parameter vector construction time=%.2f seconds"
                      % (scenario_ph_parameters_end_time - \
                         scenario_ph_parameters_start_time))

            # create symbol maps for easy storage/transmission of
            # variable values
            # NOTE: Not sure of the timing overhead that comes with
            #       this, but it's likely we can make this optional
            #       when we are not running parallel PH.
            if self._verbose:
                print("Creating deterministic SymbolMaps for scenario instances")
            scenario_ph_symbol_maps_start_time = time.time()
            # Define for what components we generate symbols
            symbol_ctypes = (Var, Suffix)
            self._create_instance_symbol_maps(symbol_ctypes)
            scenario_ph_symbol_maps_end_time = time.time()
            if self._output_times:
                print("PH SymbolMap creation time=%.2f seconds"
                      % (scenario_ph_symbol_maps_end_time - \
                         scenario_ph_symbol_maps_start_time))

            # form the ph objective weight and proximal expressions
            # Note: The Expression objects for the weight and proximal
            #       terms will be added to the instances objectives
            #       but will be assigned values of 0.0, so that the
            #       original objective function form is maintained.
            #       The purpose is so that we can use this shared
            #       Expression object in the bundle binding instance
            #       objectives as well when we call
            #       _form_bundle_binding_instances a few lines down
            #       (so regeneration of bundle objective expressions
            #       is no longer required before each iteration k
            #       solve).
            self.add_ph_objective_weight_terms()
            self.deactivate_ph_objective_weight_terms(transmit=False)
            if self._drop_proximal_terms is False:
                self.add_ph_objective_proximal_terms()
                self.deactivate_ph_objective_proximal_terms(transmit=False)

            # if we have bundles and are not running with PH Pyro, we
            # need to create the binding instances - because we are
            # responsible for farming the instances out for solution.
            if self._scenario_tree.contains_bundles():
                self._form_bundle_binding_instances(preprocess_objectives=False)

        # If specified, run the user script to collect aggregate
        # scenario data. This can slow down PH initialization as
        # syncronization across all phsolverservers is required
        if self._aggregate_getter is not None:

            if isPHPyro:

                # Transmit invocation to phsolverservers
                print("Transmitting user aggregate callback invocations "
                      "to phsolverservers")
                if self._scenario_tree.contains_bundles():
                    for scenario_bundle in self._scenario_tree._scenario_bundles:
                        ah = transmit_external_function_invocation_to_worker(
                            self,
                            scenario_bundle._name,
                            self._aggregate_getter,
                            "ph_aggregategetter_callback",
                            invocation_type=InvocationType.\
                                            PerScenarioChainedInvocation,
                            return_action_handle=True,
                            function_args=(self._aggregate_user_data,))
                        result = self._solver_manager.wait_for(ah)
                        assert len(result) == 1
                        self._aggregate_user_data = result[0]

                else:
                    for scenario in self._scenario_tree._scenarios:
                        ah = transmit_external_function_invocation_to_worker(
                            self,
                            scenario._name,
                            self._aggregate_getter,
                            "ph_aggregategetter_callback",
                            invocation_type=InvocationType.SingleInvocation,
                            return_action_handle=True,
                            function_args=(self._aggregate_user_data,))
                        result = self._solver_manager.wait_for(ah)
                        assert len(result) == 1
                        self._aggregate_user_data = result[0]

                # Transmit final aggregate state to phsolverservers
                print("Broadcasting final aggregate data to phsolverservers")
                transmit_external_function_invocation(
                    self,
                    "coopr.pysp.ph",
                    "AggregateUserData.assign_aggregate_data",
                    invocation_type=InvocationType.SingleInvocation,
                    return_action_handles=False,
                    function_args=(self._aggregate_user_data,))

            else:

                print("Executing user aggregate getter callback function")
                for scenario in self._scenario_tree._scenarios:
                    result = self._callback_function[self._aggregate_getter](
                        self,
                        self._scenario_tree,
                        scenario,
                        self._aggregate_user_data)
                    assert len(result) == 1
                    self._aggregate_user_data = result[0]

        # if specified, run the user script to initialize variable
        # rhos at their whim.
        if self._rho_setter is not None:

            if isPHPyro:

                # Transmit invocation to phsolverservers
                print("Transmitting user rho callback invocations "
                      "to phsolverservers")
                if self._scenario_tree.contains_bundles():
                    for scenario_bundle in self._scenario_tree._scenario_bundles:
                        transmit_external_function_invocation_to_worker(
                            self,
                            scenario_bundle._name,
                            self._rho_setter,
                            "ph_rhosetter_callback",
                            invocation_type=InvocationType.PerScenarioInvocation,
                            return_action_handle=False)
                else:
                    for scenario in self._scenario_tree._scenarios:
                        transmit_external_function_invocation_to_worker(
                            self,
                            scenario._name,
                            self._rho_setter,
                            "ph_rhosetter_callback",
                            invocation_type=InvocationType.SingleInvocation,
                            return_action_handle=False)

                # NOTE: For the time being we rely on the
                #       gather_scenario_tree_data call at the end this
                #       initialize method in order to collect the
                #       finalized rho values

            else:

                print("Executing user rho setter callback function")
                for scenario in self._scenario_tree._scenarios:
                    self._callback_function[self._rho_setter](
                        self,
                        self._scenario_tree,
                        scenario)

        # if specified, run the user script to initialize variable
        # bounds at their whim.
        if self._bound_setter is not None:

            if isPHPyro:

                # Transmit invocation to phsolverservers
                print("Transmitting user bound callback invocations to "
                      "phsolverservers")
                if self._scenario_tree.contains_bundles():
                    for scenario_bundle in self._scenario_tree._scenario_bundles:
                        transmit_external_function_invocation_to_worker(
                            self,
                            scenario_bundle._name,
                            self._bound_setter,
                            "ph_boundsetter_callback",
                            invocation_type=InvocationType.PerScenarioInvocation,
                            return_action_handle=False)
                else:
                    for scenario in self._scenario_tree._scenarios:
                        transmit_external_function_invocation_to_worker(
                            self,
                            scenario._name,
                            self._bound_setter,
                            "ph_boundsetter_callback",
                            invocation_type=InvocationType.SingleInvocation,
                            return_action_handle=False)

            else:

                print("Executing user bound setter callback function")
                for scenario in self._scenario_tree._scenarios:
                    self._callback_function[self._bound_setter](
                        self,
                        self._scenario_tree,
                        scenario)

        # at this point, the instances are complete - preprocess them!
        # BUT: only if the phpyro solver manager isn't in use.
        if not isPHPyro:

            if self._verbose:
                print("Preprocessing scenario instances")
            scenario_instance_preprocess_start_time = time.time()
            self._preprocess_scenario_instances()
            scenario_instance_preprocess_end_time = time.time()
            if self._output_times:
                print("Scenario instance preprocessing time=%.2f seconds"
                      % (scenario_instance_preprocess_end_time - \
                         scenario_instance_preprocess_start_time))
        else:

            if self._verbose:
                print("Broadcasting requests to collect scenario tree "
                      "instance data from PH solver servers")

            gather_scenario_tree_data(self, initialization_action_handles)

            if self._verbose:
                print("Scenario tree instance data successfully collected")

            if self._verbose:
                print("Broadcasting scenario tree id mapping"
                      "to PH solver servers")

            transmit_scenario_tree_ids(self)

            if self._verbose:
                print("Scenario tree ids successfully sent")

        self._objective_sense = \
            self._scenario_tree._scenarios[0]._objective_sense

        # indicate that we're ready to run.
        self._initialized = True

        if self._verbose:
            print("PH successfully created model instances for all scenarios")

        if self._verbose:
            print("PH is successfully initialized")

        if self._output_times:
            print("Cumulative initialization time=%.2f seconds"
                  % (time.time() - self._init_start_time))

        # let plugins know if they care.
        if self._verbose:
            print("Invoking post-initialization PH plugins")
        post_ph_initialization_plugin_callback_start_time = time.time()
        for plugin in self._ph_plugins:
            plugin.post_ph_initialization(self)
        post_ph_initialization_plugin_callback_end_time = time.time()
        if self._output_times:
            print("PH post-initialization plugin callback time=%.2f seconds"
                  % (post_ph_initialization_plugin_callback_end_time - \
                     post_ph_initialization_plugin_callback_start_time))

        if self._output_times:
            print("Cumulative PH initialization time=%.2f seconds"
                  % (time.time() - self._init_start_time))

        self._init_end_time = time.time()
        if self._output_times:
            print("Overall initialization time=%.2f seconds"
                  % (self._init_end_time - self._init_start_time))
            print("")

    #
    # Transmits Solver Options, Queues Solves, and Collects/Loads
    # Results... nothing more. All subproblems are expected to be
    # fully preprocessed.
    #
    def solve_subproblems(self, warmstart=False):

        iteration_start_time = time.time()

        # STEP -1: clear the gap dictionary - we don't have any results yet.
        for scenario in self._scenario_tree._scenarios:
            self._gaps[scenario._name] = undefined
        
        # STEP 0: set up all global solver options.
        if self._mipgap is not None:
            self._solver.options.mipgap = float(self._mipgap)
 
        # if running the phpyro solver server, we need to ship the
        # solver options across the pipe.
        if isinstance(self._solver_manager,
                      coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):
            solver_options = {}
            for key in self._solver.options:
                solver_options[key]=self._solver.options[key]
                
        # STEP 1: queue up the solves for all scenario sub-problems
        # we could use the same names for scenarios and bundles, but
        # we are easily confused.
        scenario_action_handle_map = {} # maps scenario names to action handles
        action_handle_scenario_map = {} # maps action handles to scenario names

        bundle_action_handle_map = {} # maps bundle names to action handles
        action_handle_bundle_map = {} # maps action handles to bundle names

        common_kwds = {
            'tee':self._output_solver_logs,
            'keepfiles':self._keep_solver_files,
            'symbolic_solver_labels':self._symbolic_solver_labels,
            'output_fixed_variable_bounds':self._write_fixed_variables}

        # TODO: suffixes are not handled equally for
        # scenario/bundles/serial/phpyro
        if isinstance(self._solver_manager,
                      coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):
            common_kwds['solver_options'] = solver_options
            common_kwds['solver_suffixes'] = []
            common_kwds['warmstart'] = warmstart
            common_kwds['cache_results'] = self._enable_solution_caching
            common_kwds['variable_transmission'] = \
                self._current_phpyro_variable_transmission
        else:
            common_kwds['verbose'] = self._verbose

        if self._scenario_tree.contains_bundles():
            
            for scenario_bundle in self._scenario_tree._scenario_bundles:
                
                if self._verbose:
                    print("Queuing solve for scenario bundle="+scenario_bundle._name)

                # and queue it up for solution - have to worry about warm-starting here.
                new_action_handle = None
                if isinstance(self._solver_manager, coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):
                    new_action_handle = self._solver_manager.queue(action="solve", 
                                                                   name=scenario_bundle._name,
                                                                   **common_kwds)
                else:
                    
                    if (self._output_times is True) and (self._verbose is False):
                        print("Solver manager queuing instance=%s" % (scenario_bundle._name))

                    if (warmstart is True) and (self._solver.warm_start_capable() is True):
                        new_action_handle = self._solver_manager.queue(self._bundle_binding_instance_map[scenario_bundle._name], 
                                                                       opt=self._solver, 
                                                                       warmstart=True, 
                                                                       **common_kwds)
                    else:
                        new_action_handle = self._solver_manager.queue(self._bundle_binding_instance_map[scenario_bundle._name], 
                                                                       opt=self._solver, 
                                                                       **common_kwds)
                
                bundle_action_handle_map[scenario_bundle._name] = new_action_handle
                action_handle_bundle_map[new_action_handle] = scenario_bundle._name 

        else:

            for scenario in self._scenario_tree._scenarios:

                if self._verbose:
                    print("Queuing solve for scenario=" + scenario._name)

                # once past iteration 0, there is always a feasible solution from which to warm-start.
                # however, you might want to disable warm-start when the solver is behaving badly (which does happen).
                new_action_handle = None
                if isinstance(self._solver_manager, coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):

                    new_action_handle = self._solver_manager.queue(action="solve", 
                                                                   name=scenario._name, 
                                                                   **common_kwds)
                else:

                    instance = scenario._instance

                    if (self._output_times is True) and (self._verbose is False):
                        print("Solver manager queuing instance=%s" % (scenario._name))

                    if (warmstart is True) and (self._solver.warm_start_capable() is True):

                        if self._extensions_suffix_list is not None:
                            new_action_handle = self._solver_manager.queue(instance, 
                                                                           opt=self._solver, 
                                                                           warmstart=True, 
                                                                           suffixes=self._extensions_suffix_list,
                                                                           **common_kwds)
                        else:
                            new_action_handle = self._solver_manager.queue(instance, 
                                                                           opt=self._solver, 
                                                                           warmstart=True, 
                                                                           **common_kwds)
                    else:

                        if self._extensions_suffix_list is not None:
                            new_action_handle = self._solver_manager.queue(instance, 
                                                                           opt=self._solver, 
                                                                           suffixes=self._extensions_suffix_list,
                                                                           **common_kwds)
                        else:
                            new_action_handle = self._solver_manager.queue(instance, 
                                                                           opt=self._solver, 
                                                                           **common_kwds)

                scenario_action_handle_map[scenario._name] = new_action_handle
                action_handle_scenario_map[new_action_handle] = scenario._name

        # STEP 3: loop for the solver results, reading them and loading
        #         them into instances as they are available.
        
        # presently user time, due to deficiency in solver plugins. ultimately
        # want wall clock time for PH reporting purposes.
        self._solve_times = {}

        if self._scenario_tree.contains_bundles():

            if self._verbose:
                print("Waiting for bundle sub-problem solves")

            num_results_so_far = 0

            while (num_results_so_far < len(self._scenario_tree._scenario_bundles)):

                bundle_action_handle = self._solver_manager.wait_any()
                bundle_results = self._solver_manager.get_results(bundle_action_handle)
                bundle_name = action_handle_bundle_map[bundle_action_handle]
                
                if isinstance(self._solver_manager, coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):                

                    if self._output_solver_results:
                        print("Results for scenario bundle="+bundle_name+":")
                        print(bundle_results)

                    if len(bundle_results) == 0:
                        if self._verbose:
                            print("Solve failed for scenario bundle="+bundle_name+"; no solutions generated")
                        return bundle_name

                    for scenario_name, scenario_solution in iteritems(bundle_results[0]):
                        scenario = self._scenario_tree._scenario_map[scenario_name]
                        scenario.update_current_solution(scenario_solution)
                        if self._enable_solution_caching:
                            self._cached_solutions[scenario_name] = scenario_solution
                else:

                    # a temporary hack - if results come back from pyro, they won't
                    # have a symbol map attached. so create one.
                    if bundle_results._symbol_map is None:
                        bundle_results._symbol_map = symbol_map_from_instance(bundle_instance)

                    bundle_instance = self._bundle_binding_instance_map[bundle_name]

                    if self._verbose:
                        print("Results obtained for bundle="+bundle_name)

                    if len(bundle_results.solution) == 0:
                        if self._verbose:
                            print("Solve failed for scenario bundle="+bundle_name+"; no solutions generated")
                        return bundle_name
 
                    if self._output_solver_results:
                        print("Results for bundle=",bundle_name)
                        bundle_results.write(num=1)

                    start_time = time.time()
                    bundle_instance.load(bundle_results,
                                         allow_consistent_values_for_fixed_vars=self._write_fixed_variables,
                                         comparison_tolerance_for_fixed_vars=self._comparison_tolerance_for_fixed_vars)

                    scenario_bundle = self._scenario_tree._scenario_bundle_map[bundle_name]
                    for scenario_name in scenario_bundle._scenario_names:
                        scenario = self._scenario_tree._scenario_map[scenario_name]
                        scenario.update_solution_from_instance()

                    if self._enable_solution_caching is True:
                        fixed_results = dict((scenario_name,tuple((instance_id, vardata.value, vardata.stale) \
                                                                      for instance_id, vardata in \
                                                                      iteritems(scenario_instance._PHInstanceSymbolMaps[Var].bySymbol) if vardata.fixed)) for \
                                                 scenario_name, scenario_instance in iteritems(self._bundle_scenario_instance_map[bundle_name]))
                        self._cached_solutions[bundle_name] = (bundle_results, fixed_results)
                    end_time = time.time()
                    if self._output_times:
                        print("Time loading results for bundle %s=%0.2f seconds" % (bundle_name, end_time-start_time))

                if self._verbose:
                    print("Successfully loaded solution for bundle="+bundle_name)

                num_results_so_far = num_results_so_far + 1

        else:

            if self._verbose:
                print("Waiting for scenario sub-problem solves")

            num_results_so_far = 0

            while (num_results_so_far < len(self._scenario_tree._scenarios)):

                action_handle = self._solver_manager.wait_any()
                results = self._solver_manager.get_results(action_handle)
                scenario_name = action_handle_scenario_map[action_handle]
                scenario = self._scenario_tree._scenario_map[scenario_name]

                if isinstance(self._solver_manager, coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):

                    if self._output_solver_results:
                        print("Results for scenario= "+scenario_name)

                    # TODO: Use these keywords to perform some validation of fixed variable
                    #       values in the results returned
                    ###allow_consistent_values_for_fixed_vars=self._write_fixed_variables,
                    ###comparison_tolerance_for_fixed_vars=self._comparison_tolerance_for_fixed_vars
                    # results[0] are variable values
                    # results[1] are suffix values
                    # results[2] are auxilliary values
                    scenario.update_current_solution(results[0])
                    if self._enable_solution_caching:
                        self._cached_solutions[scenario_name] = results[0]

                    auxilliary_values = results[2]
                    if "gap" in auxilliary_values:
                        self._gaps[scenario_name] = auxilliary_values["gap"]
                    else:
                        self._gaps[scenario_name] = undefined

                    if "user_time" in auxilliary_values:
                        if (str(auxilliary_values["user_time"]) != str(undefined)) and (auxilliary_values["user_time"] != None):
                            self._solve_times[scenario_name] = float(auxilliary_values["user_time"])
                        else:
                            self._solve_times[scenario_name] = undefined

                else:

                    instance = scenario._instance

                    # a temporary hack - if results come back from pyro, they won't
                    # have a symbol map attached. so create one.
                    if results._symbol_map is None:
                        results._symbol_map = symbol_map_from_instance(instance)

                    # if the solver plugin doesn't populate the user_time field, it
                    # is by default of type UndefinedData - defined in coopr.opt.results
                    if (not isinstance(results.solver.user_time, UndefinedData)) and (results.solver.user_time != None):
                        # the solve time might be a string, or might not be - we eventually
                        # would like more consistency on this front from the solver plugins.
                        self._solve_times[scenario_name] = float(results.solver.user_time)
                    else:
                        self._solve_times[scenario_name] = undefined

                    if self._verbose:
                        print("Results obtained for scenario="+scenario_name)

                    if len(results.solution) == 0:
                        if self._verbose:
                            print("Solve failed for scenario="+scenario_name+"; no solutions generated")
                        return scenario_name

                    if self._output_solver_results:
                        print("Results for scenario="+scenario_name)
                        results.write(num=1)

                    start_time = time.time()
                    
                    # TBD: Technically, we should validate that there is only
                    #      a single solution. Or at least warn if there are multiple.

                    instance.load(results,
                                  allow_consistent_values_for_fixed_vars=self._write_fixed_variables,
                                  comparison_tolerance_for_fixed_vars=self._comparison_tolerance_for_fixed_vars)
                    scenario.update_solution_from_instance()
                    if self._enable_solution_caching is True:
                        fixed_results = tuple((instance_id, vardata.value, vardata.stale) \
                                                  for instance_id, vardata in \
                                                  iteritems(instance._PHInstanceSymbolMaps[Var].bySymbol) if vardata.fixed)
                        self._cached_solutions[scenario_name] = (results, fixed_results)

                    solution0 = results.solution(0)
                    if hasattr(solution0, "gap"):
                        self._gaps[scenario_name] = solution0.gap
                    else:
                        self._gaps[scenario_name] = undefined

                    end_time = time.time()

                    if self._output_times:
                        print("Time loading results into instance %s=%0.2f seconds" % (scenario_name, end_time-start_time))

                if self._verbose:
                    print("Successfully loaded solution for scenario="+scenario_name)

                num_results_so_far = num_results_so_far + 1

        if len(self._solve_times) > 0:
            # if any of the solve times are of type coopr.opt.results.container.UndefinedData, 
            # then don't output timing statistics.
            undefined_detected = False
            for this_time in itervalues(self._solve_times):
                if isinstance(this_time, UndefinedData):
                    undefined_detected=True
            if undefined_detected:
                print("At least one scenario sub-problem solve time was undefined - skipping timing statistics")
            else:
                print("Sub-problem solve time statistics - Min: %0.2f Avg: %0.2f Max: %0.2f (seconds)" % (min(self._solve_times.values()), 
                                                                                                          sum(self._solve_times.values())/float(len(self._solve_times.values())), 
                                                                                                          max(self._solve_times.values())))
#                print "**** SOLVE TIMES:",self._solve_times.values()
#                print "*** GAPS:",sorted(self._gaps.values())

        iteration_end_time = time.time()
        self._cumulative_solve_time += (iteration_end_time - iteration_start_time)

        if self._output_times:
            print("Sub-problem solve time=%.2f seconds" % (iteration_end_time - iteration_start_time))


    """ Perform the non-weighted scenario solves and form the initial w and xbars.
    """
    def iteration_0_solves(self):

        # return None unless a sub-problem failure is detected, then
        # return its name immediately

        if self._verbose:
            print("------------------------------------------------")
            print("Starting PH iteration 0 solves")

        # scan any variables fixed prior to iteration 0, set up the
        # appropriate flags for pre-processing, and - if appropriate -
        # transmit the information to the PH solver servers.
        self._push_fixed_to_instances()

        if isinstance(self._solver_manager,
                      coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):

            # Tell the phsolverserver to include values of every
            # nonstale variable on the scenario tree. This will allow
            # us to cleanup up the scenario tree of stale unused
            # variables if desired.
            self._current_phpyro_variable_transmission = \
                TransmitType.all_stages | \
                TransmitType.derived | \
                TransmitType.blended

        else:

            # STEP 0.5: preprocess all scenario instances, as needed.
            #           if a PH pyro solver manager is being used,
            #           skip this step - the instances are never
            #           written, so need for preprocessing.
            self._preprocess_scenario_instances()

        self.solve_subproblems(warmstart=False)
        
        if self._verbose:
            print("Successfully completed PH iteration 0 solves "
                  "- solution statistics:")
            print("         Scenario                                 "
                  "Cost Objective                        Value       "
                  "Gap"),
            if self._output_times:
                print("       Solve Time")
            else:
                print("")
            for scenario in self._scenario_tree._scenarios:
                objective_value = scenario._objective
                objective_name = scenario._objective_name
                gap = self._gaps[scenario._name]
                if (not isinstance(gap,UndefinedData)) and \
                   (gap is not None):
                    print("%20s       %50s     %14.4f   %14.4f"
                          % (scenario._name,
                             objective_name,
                             objective_value,
                             gap)),
                else:
                    print("%20s       %50s     %14.4f   %14s"
                          % (scenario._name,
                             objective_name,
                             objective_value,
                             "None Reported")),
                if self._output_times:
                    solve_time = self._solve_times[scenario._name]
                    print("     %7.2f"
                          % self._solve_times[scenario._name])
                else:
                    print("")
            print("------------------------------------------------")

    #
    # recompute the averages, minimum, and maximum statistics for all
    # variables to be blended by PH, i.e., not appearing in the final
    # stage. technically speaking, the min/max aren't required by PH,
    # but they are used often enough to warrant their computation and
    # it's basically free if you're computing the average.
    #
    # **When compute_xbars is False, the xbar is not assigned the
    #   calculated node averages. The instance parameters are still
    #   updated to the current value of xbar as usual. The dual ph
    #   algorithm uses both versions of this method
    #

    def update_variable_statistics(self, compute_xbars=True):

        start_time = time.time()
        # cache the lookups - don't want to do them deep in the index loop.
        overrelax = self._overrelax
        current_iteration = self._current_iteration

        # skip the last stage, as there is only a single scenario there - no
        # meaningful statistics required!
        for stage in self._scenario_tree._stages[:-1]:

            for tree_node in stage._tree_nodes:

                xbars = tree_node._xbars

                scenario_solutions = \
                    [(scenario._probability, scenario._x[tree_node._name]) \
                     for scenario in tree_node._scenarios]

                for variable_id in tree_node._standard_variable_ids:

                    stale = False
                    values = []
                    avg_value = 0.0
                    for probability, var_values in scenario_solutions:
                        val = var_values[variable_id]
                        if val is not None:
                            avg_value += probability * val
                            values.append(val)
                        else:
                            stale = True

                    if not stale:

                        avg_value /= tree_node._probability
                        tree_node._minimums[variable_id] = min(values)
                        tree_node._maximums[variable_id] = max(values)
                        tree_node._averages[variable_id] = avg_value

                        if compute_xbars:
                            if (overrelax) and (current_iteration >= 1):
                                xbars[variable_id] = self._nu*avg_value + (1-self._nu)*var_xbar
                            else:
                                xbars[variable_id] = avg_value

        end_time = time.time()
        self._cumulative_xbar_time += (end_time - start_time)

        if self._output_times:
            print("Variable statistics compute time=%.2f seconds" % (end_time - start_time))

    def update_weights(self):
        
        start_time = time.time()
        
        # because the weight updates rely on the xbars, and the xbars
        # are node-based, I'm looping over the tree nodes and pushing
        # weights into the corresponding scenarios.
        start_time = time.time()
        
        # NOTE: the following code has some optimizations that are not
        #       normally recommended, in particular the direct access
        #       and manipulation of parameters via the .value
        #       attribute instead of the user-level-preferred value()
        #       method. this is justifiable in this particular
        #       instance because we are creating the PH parameters
        #       (and therefore can manipulate them safely), and this
        #       routine takes a non-trivial amount of the overall
        #       run-time.
        
        # cache the lookups - don't want to do them deep in the index
        # loop.
        over_relaxing = self._overrelax
        objective_sense = self._objective_sense

        # no blending over the final stage, so no weights to worry
        # about.
        for stage in self._scenario_tree._stages[:-1]:
            
            for tree_node in stage._tree_nodes:
                
                tree_node_xbars = None
                if self._dual_ph is True:
                    tree_node_xbars = tree_node._xbars
                else:
                    tree_node_xbars = tree_node._averages
                blend_values = tree_node._blend

                # These will be updated inside this loop
                tree_node_wbars = tree_node._wbars = \
                    dict((var_id,0) for var_id in tree_node._variable_ids)

                for scenario in tree_node._scenarios:
                    
                    instance = scenario._instance

                    weight_values = scenario._w[tree_node._name]
                    rho_values = scenario._rho[tree_node._name]
                    var_values = scenario._x[tree_node._name]

                    for variable_id in tree_node._standard_variable_ids:
                        
                        varval = var_values[variable_id]

                        if varval is not None:
                                
                            # we are currently not updating weights if
                            # blending is disabled for a variable.
                            # this is done on the premise that unless
                            # you are actively trying to move the
                            # variable toward the mean, the weights
                            # will blow up and be huge by the time
                            # that blending is activated.

                            nu_value = 1.0
                            if over_relaxing:
                                nu_value = self._nu
                                                                    
                            if not self._dual_ph:
                            
                                if objective_sense == minimize:
                                    weight_values[variable_id] += \
                                        blend_values[variable_id] * \
                                        rho_values[variable_id] * \
                                        nu_value * \
                                        (varval - \
                                         tree_node_xbars[variable_id])
                                else:
                                    weight_values[variable_id] -= \
                                        blend_values[variable_id] * \
                                        rho_values[variable_id] * \
                                        nu_value * \
                                        (varval - \
                                         tree_node_xbars[variable_id])
                            else:
                                # **Adding these asserts simply
                                # **because we haven't thought about
                                # **what this means for other steps in
                                # **the code
                                assert blend_values[variable_id] == 1.0
                                assert nu_value == 1.0
                                assert objective_sense == minimize
                                weight_values[variable_id] = \
                                    blend_values[variable_id] * \
                                    (rho_values[variable_id]) * \
                                    nu_value * \
                                    (varval - \
                                     tree_node_xbars[variable_id])
                                                                        
                            tree_node_wbars[variable_id] += \
                                scenario._probability * \
                                weight_values[variable_id] / tree_node._probability

        end_time = time.time()
        self._cumulative_weight_time += (end_time - start_time)
        
        if self._output_times:
            print("Weight update time=%.2f seconds" % (end_time - start_time))
            
    def update_weights_for_scenario(self, scenario):

        start_time = time.time()

        # cache the lookups - don't want to do them deep in the index
        # loop.
        over_relaxing = self._overrelax
        objective_sense = self._objective_sense

        nodeid_to_var_map = scenario._instance._ScenarioTreeSymbolMap.bySymbol

        for tree_node in scenario._node_list[:-1]:

            weight_values = scenario._w[tree_node._name]
            rho_values = scenario._rho[tree_node._name]
            var_values = scenario._x[tree_node._name]

            tree_node_xbars = None
            if self._dual_ph is True:
                tree_node_xbars = tree_node._xbars
            else:
                tree_node_xbars = tree_node._averages
            blend_values = tree_node._blend

            # Note: This does not update wbar
            for variable_id in tree_node._standard_variable_ids:

                varval = var_values[variable_id]

                if varval is not None:

                    # we are currently not updating weights if
                    # blending is disabled for a variable.  this is
                    # done on the premise that unless you are actively
                    # trying to move the variable toward the mean, the
                    # weights will blow up and be huge by the time
                    # that blending is activated.
                    
                    nu_value = 1.0
                    if over_relaxing:
                        nu_value = self._nu

                    if self._dual_ph is False:
                        if objective_sense == minimize:
                            weight_values[variable_id] += \
                                blend_values[variable_id] * \
                                rho_values[variable_id] * \
                                nu_value * \
                                (varval - \
                                 tree_node_xbars[variable_id])
                        else:
                            weight_values[variable_id] -= \
                                blend_values[variable_id] * \
                                rho_values[variable_id] * \
                                nu_value * \
                                (varval - \
                                 tree_node_xbars[variable_id])
                    else:
                        # **Adding these asserts simply because we
                        # **haven't thought about what this means for
                        # **other steps in the code
                        assert blend_values[variable_id] == 1.0
                        assert nu_value == 1.0
                        assert objective_sense == minimize
                        weight_values[variable_id] = \
                            blend_values[variable_id] * \
                            rho_values[variable_id] * \
                            nu_value * \
                            (varval - \
                             tree_node_xbars[variable_id])

        end_time = time.time()
        self._cumulative_weight_time += (end_time - start_time)

    def iteration_k_solves(self):

        if self._verbose:
            print("------------------------------------------------")
            print("Starting PH iteration %s solves"
                  % (self._current_iteration))

        # scan any variables fixed/freed, set up the appropriate flags
        # for pre-processing, and - if appropriate - transmit the
        # information to the PH solver servers.
        self._push_fixed_to_instances()

        # update parameters on instances (transmitting to ph solver
        # servers when appropriate)
        self._push_xbar_to_instances()
        self._push_w_to_instances()
        # NOTE: We aren't currently propagating rhos, as they
        #       generally don't change - we need to have a flag,
        #       though, indicating whether the rhos have changed, so
        #       they can be transmitted if needed.
        if (self._current_iteration == 1):
            self._push_rho_to_instances()

        # STEP -1: if using a PH solver manager, propagate current
        #          weights/averages to the appropriate solver servers.
        #          ditto the tree node statistics, which are necessary
        #          if linearizing (so an optimization could be
        #          performed here).
        if isinstance(self._solver_manager,
                      coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):

            # we only transmit tree node statistics if we are
            # linearizing the PH objectives.  otherwise, the
            # statistics are never referenced by the PH solver
            # servers, so don't want the time.
            if (self._linearize_nonbinary_penalty_terms > 0) or \
               (self._scenario_tree.contains_bundles()):
                transmit_tree_node_statistics(self)

            # Tell the phsolverserver set the variable transmission
            # setting to the default for iteration k solves
            self._current_phpyro_variable_transmission = \
                self._phpyro_default_iteration_k_variable_transmission
        else:
            # STEP 0.5: preprocess all scenario instances, if needed.
            #           if a PH pyro solver manager is being used,
            #           skip this step - the instances are never
            #           written, so need for preprocessing.
            self._preprocess_scenario_instances()

            # GAH: We may need to redefine our concept of
            #      warmstart. These values could be helpful in the
            #      nonlinear case (or could be better than 0.0, the
            #      likely default used by the solver when these
            #      initializations are not placed in the NL
            #      file. **Note: Initializations go into the NL file
            #      independent of the "warmstart" keyword

            # STEP 0.85: if linearizing the PH objective, clear the
            #            values for any PHQUADPENALTY* variables -
            #            otherwise, the MIP starts are likely to be
            #            infeasible.
            if self._linearize_nonbinary_penalty_terms > 0:
                self._reset_instance_linearization_variables()

            if self._scenario_tree.contains_bundles():
                # clear non-converged variables and stage cost
                # variables, to ensure feasible warm starts.
                reset_nonconverged_variables(self._scenario_tree, self._instances)
                reset_stage_cost_variables(self._scenario_tree, self._instances)
            else:
                # clear stage cost variables, to ensure feasible warm starts.
                reset_stage_cost_variables(self._scenario_tree, self._instances)

        self.solve_subproblems(warmstart=not self._disable_warmstarts)

        if self._verbose:
            print("Successfully completed PH iteration %s solves "
                  "- solution statistics:" % (self._current_iteration))
            print("       Scenario                   PH Objective      "
                  "Cost Objective       PH Objective Gap"),
            if self._output_times:
                print("      Solve Time")
            else:
                print("")
            for scenario in self._scenario_tree._scenarios:
                objective_value = scenario._objective
                scenario_cost = scenario._cost
                gap = self._gaps[scenario._name]
                if (not isinstance(gap, UndefinedData)) and (gap is not None):
                    print("%20s       %18.4f     %14.4f      %14.4f"
                          % (scenario._name,
                             objective_value,
                             scenario_cost,
                             gap)),
                else:
                    print("%20s       %18.4f     %14.4f      %14s"
                          % (scenario._name,
                             objective_value,
                             scenario_cost,
                             "None Reported")),
                if self._output_times:
                    solve_time = self._solve_times[scenario._name]
                    if (not isinstance(solve_time, UndefinedData)) and \
                       (solve_time is not None):
                        print("           %7.2f"
                              % self._solve_times[scenario._name])
                    else:
                        print("           None Reported")
                else:
                    print("")

    def async_iteration_k_plus_solves(self):
        # note: this routine retains control until a termination criterion is met
        # modified nov 2011 by dlw to do async with a window-like paramater

        if self._async_buffer_len <= 0 or self._async_buffer_len > len(self._scenario_tree._scenarios):
            raise RuntimeError("Async buffer length parameter is bad:"+str(self._async_buffer_len))
        if self._verbose == True:
            print("Starting PH iteration k+ solves - running async with buffer length=", self._async_buffer_len)

        # we are going to buffer the scenario names
        ScenarioBuffer = []

        # things progress at different rates - keep track of what's going on.
        total_scenario_solves = 0 # self-explanatory.
        scenario_ks = {} # a map of scenario name to the number of sub-problems solved thus far.
        for scenario in self._scenario_tree._scenarios:
            scenario_ks[scenario._name] = 0

        # keep track of action handles mapping to scenarios.
        action_handle_instance_map = {} # maps action handles to scenario names

        # only form the PH objective components once, before we start in on the asychronous sub-problem solves
        self.activate_ph_objective_weight_terms(transmit=False)
        if self._drop_proximal_terms is False:
            self.activate_ph_objective_proximal_terms(transmit=False)

        # if linearizing, form the necessary terms to compute the cost variables.
        if self._linearize_nonbinary_penalty_terms > 0:
            self.form_ph_linearized_objective_constraints()

        self._preprocess_scenario_instances()

        # STEP 1: queue up the solves for all scenario sub-problems.

        for scenario in self._scenario_tree._scenarios:

            instance = self._instances[scenario._name]

            if self._verbose == True:
                print("Queuing solve for scenario=" + scenario._name)

            # once past iteration 0, there is always a feasible solution from which to warm-start.
            if (self._disable_warmstarts is False) and (self._solver.warm_start_capable()):
                new_action_handle = self._solver_manager.queue(instance, 
                                                               opt=self._solver, 
                                                               warmstart=True, 
                                                               tee=self._output_solver_logs, 
                                                               verbose=self._verbose)
            else:
                new_action_handle = self._solver_manager.queue(instance, 
                                                               opt=self._solver, 
                                                               tee=self._output_solver_logs, 
                                                               verbose=self._verbose)

            action_handle_instance_map[new_action_handle] = scenario._name

        # STEP 2: wait for the first action handle to return, process it, and keep chugging.

        while(True):

            this_action_handle = self._solver_manager.wait_any()
            solved_scenario_name = action_handle_instance_map[this_action_handle]

            scenario_ks[solved_scenario_name] += 1
            total_scenario_solves += 1

            if int(total_scenario_solves / len(scenario_ks)) > self._current_iteration:
                new_reportable_iteration = True
                self._current_iteration += 1
            else:
                new_reportable_iteration = False

            if self._verbose:
                print("Solve for scenario="+solved_scenario_name+ "completed - new solve count for this scenario="+str(scenario_ks[solved_scenario_name]))

            instance = self._instances[solved_scenario_name]
            results = self._solver_manager.get_results(this_action_handle)

            if len(results.solution) == 0:
                raise RuntimeError("Solve failed for scenario="+solved_scenario_name+"; no solutions generated")

            if self._verbose:
                print("Solve completed successfully")

            if self._output_solver_results == True:
                print("Results:")
                results.write(num=1)

            # in async mode, it is possible that we will receive values for variables
            # that have been fixed due to apparent convergence - but the outstanding
            # scenario solves will obviously not know this. if the values are inconsistent,
            # we have bigger problems - an exception will be thrown, and we currently lack
            # a recourse mechanism in such a case.
            instance.load(results,
                          allow_consistent_values_for_fixed_vars=self._write_fixed_variables,
                          comparison_tolerance_for_fixed_vars=self._comparison_tolerance_for_fixed_vars)

            if self._verbose == True:
                print("Successfully loaded solution")

            # we're assuming there is a single solution.
            # the "value" attribute is a pre-defined feature of any solution - it is relative to whatever
            # objective was selected during optimization, which of course should be the PH objective.
            try:
                ph_objective_value = float(results.solution(0).objective[1].value)
            except AttributeError:
                # some solvers (e.g., through the SOL interface) don't report objective function values.
                ph_objective_value = 0.0

            if self._verbose:
                print("%20s       %18.4f     %14.4f" % (solved_scenario_name, ph_objective_value, 0.0))

            # changed 19 Nov 2011 to support scenario buffers for async
            ScenarioBuffer.append(solved_scenario_name)
            if len(ScenarioBuffer) == self._async_buffer_len:
                if self._verbose:
                    print("Processing async buffer.")
                    
                # update variable statistics prior to any output.
                self.update_variable_statistics()
                for scenario_name in ScenarioBuffer:
                    scenario = self._scenario_tree.get_scenario(scenario_name)
                    self.update_weights_for_scenario(scenario)
                    scenario.push_w_to_instance()

                # we don't want to report stuff and invoke callbacks after each scenario solve - wait
                # for when each scenario (on average) has reported back a solution.
                if new_reportable_iteration:

                    # let plugins know if they care.
                    for plugin in self._ph_plugins:
                        plugin.post_iteration_k_solves(self)

                    # update the fixed variable statistics.
                    (self._total_fixed_discrete_vars,self._total_fixed_continuous_vars) = self.compute_fixed_variable_counts()

                    if self._verbose:
                        print("Async Reportable Iteration Current variable averages and weights:")
                        self.pprint(True,True,False,False, output_only_nonconverged=self._report_only_nonconverged_variables)

                    # check for early termination.
                    self._converger.update(self._current_iteration, self, self._scenario_tree, self._instances)
                    first_stage_min, first_stage_avg, first_stage_max = self._extract_first_stage_cost_statistics()
                    print("Convergence metric=%12.4f  First stage cost avg=%12.4f  Max-Min=%8.2f" % (self._converger.lastMetric(), first_stage_avg, first_stage_max-first_stage_min))

                    if self._converger.isConverged(self):
                        if self._total_discrete_vars == 0:
                            print("PH converged - convergence metric is below threshold="+str(self._converger._convergence_threshold))
                        else:
                            print("PH converged - convergence metric is below threshold="+str(self._converger._convergence_threshold)+" or all discrete variables are fixed")
                        break

                # see if we've exceeded our patience with the iteration limit.
                # changed to be based on the average on July 10, 2011 by dlw
                # (really, it should be some combination of the min and average over the scenarios)
                if total_scenario_solves / len(self._scenario_tree._scenarios) >= self._max_iterations:
                    return

                # update parameters on instances
                self._push_xbar_to_instances()
                self._push_w_to_instances()

                # we're still good to run - re-queue the instance, following any necessary linearization 
                for  scenario_name in ScenarioBuffer:
                    instance = self._instances[scenario_name]

                    # if linearizing, form the necessary terms to compute the cost variables.
                    if self._linearize_nonbinary_penalty_terms > 0:
                        new_attrs = form_linearized_objective_constraints(scenario_name,
                                                                          instance,
                                                                          self._scenario_tree,
                                                                          self._linearize_nonbinary_penalty_terms,
                                                                          self._breakpoint_strategy,
                                                                          self._integer_tolerance)
                        self._problem_states.ph_constraints[scenario_name].extend(new_attrs)
                        # Flag the preprocessor
                        self._problem_states.ph_constraints_updated[scenario_name] = True

                    # preprocess prior to queuing the solve.
                    preprocess_scenario_instance(instance,
                                                 self._problem_states.fixed_variables[scenario_name],
                                                 self._problem_states.freed_variables[scenario_name],
                                                 self._problem_states.user_constraints_updated[scenario_name],
                                                 self._problem_states.ph_constraints_updated[scenario_name],
                                                 self._problem_states.ph_constraints[scenario_name],
                                                 self._problem_states.objective_updated[scenario_name],
                                                 not self._write_fixed_variables,
                                                 self._solver)

                    # We've preprocessed the instance, reset the relevant flags
                    self._problem_states.clear_update_flags(scenario_name)
                    self._problem_states.clear_fixed_variables(scenario_name)
                    self._problem_states.clear_freed_variables(scenario_name)

                    # once past the initial sub-problem solves, there is always a feasible solution from which to warm-start.
                    if (self._disable_warmstarts is False) and (self._solver.warm_start_capable()):
                        new_action_handle = self._solver_manager.queue(instance, 
                                                                       opt=self._solver, 
                                                                       warmstart=True, 
                                                                       tee=self._output_solver_logs, 
                                                                       verbose=self._verbose)
                    else:
                        new_action_handle = self._solver_manager.queue(instance, 
                                                                       opt=self._solver, 
                                                                       tee=self._output_solver_logs, 
                                                                       verbose=self._verbose)

                    action_handle_instance_map[new_action_handle] = scenario_name

                    if self._verbose:
                        print("Queued solve k="+str(scenario_ks[scenario_name]+1)+" for scenario="+solved_scenario_name)

                    if self._verbose:
                        for sname, scenario_count in iteritems(scenario_ks):
                            print("Scenario="+sname+" was solved "+str(scenario_count)+" times")
                        print("Cumulative number of scenario solves="+str(total_scenario_solves))
                        print("PH Iteration Count (computed)="+str(self._current_iteration) )

                    if self._verbose:
                        print("Variable values following scenario solves:")
                        self.pprint(False,False,True,False,output_only_nonconverged=self._report_only_nonconverged_variables)

                if self._verbose is True:
                    print("Emptying the asynch scenario buffer.")
                # this is not a speed issue, is there a memory issue?
                ScenarioBuffer = []

    def solve(self):
        # return None unless a solve failure was detected in iter0, then immediately return the iter0 solve return value 
        # (which should be the name of the scenario detected)

        self._solve_start_time = time.time()
        self._cumulative_solve_time = 0.0
        self._cumulative_xbar_time = 0.0
        self._cumulative_weight_time = 0.0
        self._current_iteration = 0;

        print("Starting PH")

        if self._initialized == False:
            raise RuntimeError("PH is not initialized - cannot invoke solve() method")

        # garbage collection noticeably slows down PH when dealing with
        # large numbers of scenarios. fortunately, there are well-defined
        # points at which garbage collection makes sense (and there isn't a
        # lot of collection to do). namely, after each PH iteration.
        re_enable_gc = gc.isenabled()
        gc.disable()

        print("")
        print("Initiating PH iteration=" + str(self._current_iteration))

        iter0retval = self.iteration_0_solves()
        
        if iter0retval is not None:
            if self._verbose:
                print("Iteration zero reports trouble with scenario: "
                      +str(iter0retval))
            return iter0retval

        # now that we have scenario solutions, compute and cache the
        # number of discrete and continuous variables.  the values are
        # of general use, e.g., in the converger classes and in
        # plugins. this is only invoked once, after the iteration 0
        # solves.
        (self._total_discrete_vars,self._total_continuous_vars) = \
            self.compute_blended_variable_counts()

        if self._verbose:
            print("Total number of non-stale discrete instance variables="
                  +str(self._total_discrete_vars))
            print("Total number of non-stale continuous instance variables="
                  +str(self._total_continuous_vars))

        # very rare, but the following condition can actually happen...
        if (self._total_discrete_vars + self._total_continuous_vars) == 0:
            raise RuntimeError("***ERROR: The total number of non-anticipative "
                               "discrete and continuous variables equals 0! "
                               "Did you set the StageVariables set(s) in "
                               "ScenarioStructure.dat")

        # update variable statistics prior to any output, and  
        # most importantly, prior to any variable fixing by 
        # PH extensions.
        self.update_variable_statistics()

        if (self._verbose) or (self._report_solutions):
            print("Variable values following scenario solves:")
            self.pprint(False, False, True, False, output_only_statistics=self._report_only_statistics, output_only_nonconverged=self._report_only_nonconverged_variables)

        # let plugins know if they care.   
        for plugin in self._ph_plugins:   
            plugin.post_iteration_0_solves(self)
        
        # update the fixed variable statistics.
        (self._total_fixed_discrete_vars,self._total_fixed_continuous_vars) = self.compute_fixed_variable_counts()

        print("Number of discrete variables fixed="+str(self._total_fixed_discrete_vars)+" (total="+str(self._total_discrete_vars)+")")
        print("Number of continuous variables fixed="+str(self._total_fixed_continuous_vars)+" (total="+str(self._total_continuous_vars)+")")

        # always output the convergence metric and first-stage cost statistics, to give a sense of progress.
        self._converger.update(self._current_iteration, self, self._scenario_tree, self._instances)
        first_stage_min, first_stage_avg, first_stage_max = self._extract_first_stage_cost_statistics()
        print("Convergence metric=%12.4f  First stage cost avg=%12.4f  Max-Min=%8.2f" % (self._converger.lastMetric(), first_stage_avg, first_stage_max-first_stage_min))

        # let plugins know if they care.   
        for plugin in self._ph_plugins:   
            plugin.post_iteration_0(self)

        # IMPT: update the weights after the PH iteration 0 callbacks - they might compute rhos based on iteration 0 solutions.
        if self._ph_weight_updates_enabled:
            self.update_weights()

        # checkpoint if it's time - which it always is after iteration 0,
        # if the interval is >= 1!
        if (self._checkpoint_interval > 0):
            self.checkpoint(0)

        # garbage-collect if it wasn't disabled entirely.
        if re_enable_gc:
            if (time.time() - self._time_since_last_garbage_collect) >= self._minimum_garbage_collection_interval:
               gc.collect()
               self._time_last_garbage_collect = time.time() 

        # everybody wants to know how long they've been waiting...
        print("Cumulative run-time=%.2f seconds" % (time.time() - self._solve_start_time))

        # gather memory statistics (for leak detection purposes) if specified.
        # XXX begin debugging - commented
        #if (pympler_available) and (self._profile_memory >= 1):
        #    objects_last_iteration = muppy.get_objects()
        #    summary_last_iteration = summary.summarize(objects_last_iteration)
        # XXX end debugging - commented
 
        ####################################################################################################
        # major logic branch - if we are not running async, do the usual PH - otherwise, invoke the async. #
        ####################################################################################################
        if self._async is False:

            # Note: As a first pass at our implementation, the solve method
            #       on the DualPHModel actually updates the xbar dictionary
            #       on the ph scenario tree.
            if (self._dual_ph is True):
                # FIXME: Remove from dual ph options list
                if self._drop_proximal_terms is True:
                    raise RuntimeError("The option '--drop-proximal-terms' is not allowed with dual ph.")
                WARM_START = True
                dual_model = DualPHModel(self)
                print("Warm-starting dual-ph weights")
                if WARM_START is True:
                    self.activate_ph_objective_proximal_terms(transmit=True)

                    self.iteration_k_solves()
                    dual_model.add_cut(first=True)
                    dual_model.solve()
                    self.update_variable_statistics(compute_xbars=False)
                    self.update_weights()

                    self.deactivate_ph_objective_weight_terms(transmit=True)
                    self.activate_ph_objective_proximal_terms(transmit=True)
                else:
                    dual_model.add_cut()
                    dual_model.solve()
                    self.update_variable_statistics(compute_xbars=False)
                    self.update_weights()

                    self.activate_ph_objective_proximal_terms(transmit=True)
            else:
                self.activate_ph_objective_weight_terms(transmit=True)
                if self._drop_proximal_terms is False:
                    self.activate_ph_objective_proximal_terms(transmit=True)
                

            ####################################################################################################

            # there is an upper bound on the number of iterations to execute -
            # the actual bound depends on the converger supplied by the user.
            for i in xrange(1, self._max_iterations+1):

                # XXX begin debugging
                #def muppetize(self):
                #    if (pympler_available) and (self._profile_memory >= 1):
                #        objects_this_iteration = muppy.get_objects()
                #        summary_this_iteration = summary.summarize(objects_this_iteration)
                #        summary.print_(summary_this_iteration)
                #        del summary_this_iteration
                # XXX end debugging

                self._current_iteration = self._current_iteration + 1

                print("")
                print("Initiating PH iteration=" + str(self._current_iteration))

                if (self._verbose) or (self._report_weights):
                    print("Variable averages and weights prior to scenario solves:")
                    self.pprint(True, True, False, False,
                                output_only_statistics=self._report_only_statistics,
                                output_only_nonconverged=self._report_only_nonconverged_variables)

                # let plugins know if they care.
                for plugin in self._ph_plugins:
                    plugin.pre_iteration_k_solves(self)

                # with the introduction of piecewise linearization, the form of the
                # penalty-weighted objective is no longer fixed. thus, when linearizing,
                # we need to construct (or at least modify) the constraints used to
                # compute the linearized cost terms.
                if self._linearize_nonbinary_penalty_terms > 0:
                    self.form_ph_linearized_objective_constraints()

                self.iteration_k_solves()
                
                # update variable statistics prior to any output.
                if self._dual_ph is False:
                    self.update_variable_statistics()
                else:
                    dual_rc = dual_model.add_cut()
                    dual_model.solve()
                    self.update_variable_statistics(compute_xbars=False)

                # we don't technically have to do this at the last iteration,
                # but with checkpointing and re-starts, you're never sure
                # when you're executing the last iteration.
                if self._ph_weight_updates_enabled:
                    self.update_weights()

                # let plugins know if they care.
                for plugin in self._ph_plugins:
                    plugin.post_iteration_k_solves(self)

                if (self._verbose) or (self._report_solutions):
                    print("Variable values following scenario solves:")
                    self.pprint(False, False, True, False, output_only_statistics=self._report_only_statistics, output_only_nonconverged=self._report_only_nonconverged_variables)

                # update the fixed variable statistics.
                self._total_fixed_discrete_vars,self._total_fixed_continuous_vars = \
                    self.compute_fixed_variable_counts()

                print("Number of discrete variables fixed="
                      +str(self._total_fixed_discrete_vars)+" "
                      "(total="+str(self._total_discrete_vars)+")")
                print("Number of continuous variables fixed="
                      +str(self._total_fixed_continuous_vars)+" "
                      "(total="+str(self._total_continuous_vars)+")")

                # update the convergence statistic - prior to the
                # plugins callbacks; technically, computing the
                # convergence metric is part of the iteration k work
                # load.
                    
                self._converger.update(self._current_iteration,
                                       self,
                                       self._scenario_tree,
                                       self._instances)
                first_stage_min, first_stage_avg, first_stage_max = \
                    self._extract_first_stage_cost_statistics()
                print("Convergence metric=%12.4f  First stage cost avg=%12.4f  "
                      "Max-Min=%8.2f" % (self._converger.lastMetric(),
                                         first_stage_avg,
                                         first_stage_max-first_stage_min))

                # let plugins know if they care.
                for plugin in self._ph_plugins:
                    plugin.post_iteration_k(self)

                # at this point, all the real work of an iteration is
                # complete.

                # checkpoint if it's time.
                if (self._checkpoint_interval > 0) and \
                   (i % self._checkpoint_interval is 0):
                    self.checkpoint(i)

                # everybody wants to know how long they've been waiting...
                print("Cumulative run-time=%.2f seconds"
                      % (time.time() - self._solve_start_time))

                # check for early termination.
                if self._dual_ph is False:
                    if self._converger.isConverged(self):
                        if self._total_discrete_vars == 0:
                            print("PH converged - convergence metric is below "
                                  "threshold="
                                  +str(self._converger._convergence_threshold))
                        else:
                            print("PH converged - convergence metric is below "
                                  "threshold="
                                  +str(self._converger._convergence_threshold)+" "
                                  "or all discrete variables are fixed")
                        break
                else:
                    # This is ugly. We can fix later when we figure
                    # out convergence criteria for the dual ph
                    # algorithm
                    if dual_rc is True:
                        break

                # if we're terminating due to exceeding the maximum
                # iteration count, print a message indicating so -
                # otherwise, you get a quiet, information-free output
                # trace.
                if i == self._max_iterations:
                    print("Halting PH - reached maximal iteration count="
                          +str(self._max_iterations))

                # garbage-collect if it wasn't disabled entirely.
                if re_enable_gc:
                    if (time.time() - self._time_since_last_garbage_collect) >= \
                         self._minimum_garbage_collection_interval:
                       gc.collect()
                       self._time_since_last_garbage_collect = time.time()

                # gather and report memory statistics (for leak
                # detection purposes) if specified.
                if (guppy_available) and (self._profile_memory >= 1):
                    print(hpy().heap())

                    #print "New (persistent) objects constructed during PH iteration "+str(self._current_iteration)+":"
                    #memory_tracker.print_diff(summary1=summary_last_iteration,
                    #                          summary2=summary_this_iteration)

                    ## get ready for the next iteration.
                    #objects_last_iteration = objects_this_iteration
                    #summary_last_iteration = summary_this_iteration
                    
                    # XXX begin debugging
                    #print "Current type: {0} ({1})".format(type(self), type(self).__name__)
                    #print "Recognized objects in muppy:", len(muppy.get_objects())
                    #print "Uncollectable objects (cycles?):", gc.garbage

                    ##from pympler.muppy import refbrowser
                    ##refbrowser.InteractiveBrowser(self).main()

                    #print "Referents from PH solver:", gc.get_referents(self)
                    #print "Interesting referent keys:", [k for k in gc.get_referents(self)[0].keys() if type(gc.get_referents(self)[0][k]).__name__ not in ['list', 'int', 'str', 'float', 'dict', 'bool']]
                    #print "_ph_plugins:", gc.get_referents(self)[0]['_ph_plugins']
                    #print "_converger:", gc.get_referents(self)[0]['_converger']
                    # XXX end debugging

            ####################################################################################################

        else:
            # TODO: Eliminate this option from the rundph command
            if self._dual_ph is True:
                raise NotImplementedError("The 'async' option has not been implemented for dual ph.")
            ####################################################################################################
            self.async_iteration_k_plus_solves()
            ####################################################################################################

        # re-enable the normal garbage collection mode.
        if re_enable_gc:
            gc.enable()

        print("Number of discrete variables fixed before final plugin calls="+str(self._total_fixed_discrete_vars)+" (total="+str(self._total_discrete_vars)+")")
        print("Number of continuous variables fixed before final plugin calls="+str(self._total_fixed_continuous_vars)+" (total="+str(self._total_continuous_vars)+")")

        if isinstance(self._solver_manager, coopr.solvers.plugins.smanager.phpyro.SolverManager_PHPyro):
            collect_full_results(self,
                                 TransmitType.all_stages | \
                                 TransmitType.blended | \
                                 TransmitType.derived | \
                                 TransmitType.fixed)

        # let plugins know if they care. do this before
        # the final solution / statistics output, as the plugins
        # might do some final tweaking.
        for plugin in self._ph_plugins:
            plugin.post_ph_execution(self)

        # update the fixed variable statistics - the plugins might have done something.
        (self._total_fixed_discrete_vars,self._total_fixed_continuous_vars) = self.compute_fixed_variable_counts()

        self._solve_end_time = time.time()

        print("PH complete")

        print("Convergence history:")
        self._converger.pprint()

        # print *the* metric of interest.
        print("")
        print("***********************************************************************************************")
        root_node = self._scenario_tree._stages[0]._tree_nodes[0]      
        print(">>>THE EXPECTED SUM OF THE STAGE COST VARIABLES="+str(root_node.computeExpectedNodeCost())+"<<<")
        print(">>>***CAUTION***: Assumes full (or nearly so) convergence of scenario solutions at each node in the scenario tree - computed costs are invalid otherwise<<<")
        print("***********************************************************************************************")

        print("Final number of discrete variables fixed="+str(self._total_fixed_discrete_vars)+" (total="+str(self._total_discrete_vars)+")")
        print("Final number of continuous variables fixed="+str(self._total_fixed_continuous_vars)+" (total="+str(self._total_continuous_vars)+")")

        # populate the scenario tree solution from the instances - to ensure consistent state
        # across the scenario tree instance and the scenario instances.
        self._scenario_tree.snapshotSolutionFromScenarios()

        print("Final variable values:")
        self.pprint(False, False, True, True, output_only_statistics=self._report_only_statistics, output_only_nonconverged=self._report_only_nonconverged_variables)

        print("Final costs:")
        self._scenario_tree.pprintCosts()

        if self._output_scenario_tree_solution:
            print("Final solution (scenario tree format):")
            self._scenario_tree.pprintSolution()

        if (self._verbose) and (self._output_times):
            print("Overall run-time=%.2f seconds" % (self._solve_end_time - self._solve_start_time))

        for tree_node in self._scenario_tree._tree_nodes:
            if tree_node.has_fixed_in_queue() or \
               tree_node.has_freed_in_queue():
                print("***WARNING***: PH exiting with fixed or freed variables "
                      "in the scenario tree queue whose statuses have not been "
                      "pushed to the scenario instances. This is because these "
                      "requests were placed in the queue after the most recent "
                      "solve. If these statuses are pushed to the scenario "
                      "instances, a new solution should be obtained in order to "
                      "reflect accurate solution data within the scenario tree.")
                break

        # cleanup the scenario instances for post-processing - ideally, we want to leave them in
        # their original state, minus all the PH-specific stuff. we don't do all cleanup (leaving
        # things like rhos, etc), but we do clean up constraints, as that really hoses up the ef
        # writer.
        self._cleanup_scenario_instances()
        self._preprocess_scenario_instances()
        self._clear_bundle_instances()

    def _clear_bundle_instances(self):
        
        for bundle_name, bundle_instance in iteritems(self._bundle_binding_instance_map):
            for scenario_name in self._bundle_scenario_instance_map[bundle_name]:
                bundle_instance.del_component(scenario_name)

        self._bundle_binding_instance_map = {}
        self._bundle_scenario_instance_map = {}
    #
    # prints a summary of all collected time statistics
    #

    def print_time_stats(self):

        print("PH run-time statistics:")

        print("Initialization time=  %.2f seconds" % (self._init_end_time - self._init_start_time))
        print("Overall solve time=   %.2f seconds" % (self._solve_end_time - self._solve_start_time))
        print("Scenario solve time=  %.2f seconds" % self._cumulative_solve_time)
        print("Average update time=  %.2f seconds" % self._cumulative_xbar_time)
        print("Weight update time=   %.2f seconds" % self._cumulative_weight_time)

    #
    # a utility to determine whether to output weight / average / etc. information for
    # a variable/node combination. when the printing is moved into a callback/plugin,
    # this routine will go there. for now, we don't dive down into the node resolution -
    # just the variable/stage.
    #

    def should_print(self, stage, variable):

        if self._output_continuous_variable_stats is False:

            variable_type = variable.domain

            if (isinstance(variable_type, IntegerSet) is False) and (isinstance(variable_type, BooleanSet) is False):

                return False

        return True

    #
    # pretty-prints the state of the current variable averages, weights, and values.
    # inputs are booleans indicating which components should be output.
    #

    def pprint(self,
               output_averages,
               output_weights,
               output_values,
               output_fixed,
               output_only_statistics=False,
               output_only_nonconverged=False):

        if self._initialized is False:
            raise RuntimeError("PH is not initialized - cannot invoke pprint() method")

        # print tree nodes and associated variable/xbar/ph information in stage-order
        # we don't blend in the last stage, so we don't current care about printing the associated information.
        for stage in self._scenario_tree._stages[:-1]:

            print("   Stage: " + str(stage._name))

            num_outputs_this_stage = 0 # tracks the number of outputs on a per-index basis.

            for variable_name, index_template in iteritems(stage._variables):

                num_outputs_this_variable = 0 # track, so we don't output the variable names unless there is an entry to report.

                for tree_node in stage._tree_nodes:

                    if output_only_statistics is False:
                        sys.stdout.write("          (Scenarios: ")
                        for scenario in tree_node._scenarios:
                            sys.stdout.write(scenario._name+"  ")
                            if scenario == tree_node._scenarios[-1]:
                                sys.stdout.write(")\n")

                    variable_indices = tree_node._variable_indices[variable_name]

                    # this is moderately redundant, but shouldn't show up in profiles - 
                    # printing takes more time than computation. determine the maximimal
                    # index string length, so we can output readable column formats.
                    max_index_string_length = 0
                    for index in variable_indices:
                        if index != None:
                            this_index_length = len(indexToString(index))
                            if this_index_length > max_index_string_length:
                                max_index_string_length = this_index_length

                    for index in sorted(variable_indices):

                        num_outputs_this_index = 0 # track, so we don't output the variable index more than once.

                        # determine if the variable/index pair is used across the set of scenarios (technically,
                        # it should be good enough to check one scenario). ditto for "fixed" status. fixed does
                        # imply unused (see note below), but we care about the fixed status when outputting
                        # final solutions.

                        # should be consistent across scenarios, so one "unused" flags as invalid.
                        variable_id = tree_node._name_index_to_id[variable_name,index]
                        is_fixed = tree_node.is_variable_fixed(variable_id)
                        
                        is_not_stale = all((not scenario.is_variable_stale(tree_node, variable_id)) \
                                           for scenario in tree_node._scenarios)

                        # IMPT: this is far from obvious, but variables that are fixed will - because
                        #       presolve will identify them as constants and eliminate them from all
                        #       expressions - be flagged as "unused" and therefore not output.

                        if ((output_fixed) and (is_fixed)) or ((is_not_stale) and (not is_fixed)):

                            minimum_value = tree_node._minimums[variable_id]
                            average_value = tree_node._averages[variable_id]
                            maximum_value = tree_node._maximums[variable_id]

                            # there really isn't a default need to output variables whose
                            # values are equal to 0 across-the-board. and there is good 
                            # reason not to, i.e., the volume of output.
                            if ((fabs(minimum_value) > self._integer_tolerance) or (fabs(maximum_value) > self._integer_tolerance)) or \
                               (self._report_for_zero_variable_values is True):

                                if (fabs(maximum_value - minimum_value) <= self._integer_tolerance) and (output_only_nonconverged == True):
                                    pass
                                else:
                                    num_outputs_this_stage = num_outputs_this_stage + 1
                                    num_outputs_this_variable = num_outputs_this_variable + 1
                                    num_outputs_this_index = num_outputs_this_index + 1

                                    if num_outputs_this_variable == 1:
                                        sys.stdout.write("      Variable: " + variable_name+'\n')

                                    if num_outputs_this_index == 1:
                                        if index is not None:
                                            format_string = "         Index: %"+str(max_index_string_length)+"s"
                                            sys.stdout.write(format_string % indexToString(index))

                                    if len(stage._tree_nodes) > 1:
                                        sys.stdout.write("\n")
                                        sys.stdout.write("         Tree Node: "+tree_node._name)

                                    if output_values:
                                        if output_only_statistics is False:
                                            sys.stdout.write("\tValues:  ")
                                        last_scenario = tree_node._scenarios[-1]
                                        for scenario in tree_node._scenarios:
                                            scenario_probability = scenario._probability
                                            this_value = scenario._x[tree_node._name][variable_id]
                                            if output_only_statistics is False:
                                                sys.stdout.write("%12.4f" % this_value)
                                            if scenario is last_scenario:
                                                if output_only_statistics:
                                                    # there technically isn't any good reason not to always report
                                                    # the min and max; the only reason we're not doing this currently
                                                    # is to avoid updating our regression test baseline output.
                                                    sys.stdout.write("    Min:  %12.4f" % (minimum_value))
                                                    sys.stdout.write("    Avg:  %12.4f" % (average_value))
                                                    sys.stdout.write("    Max:  %12.4f" % (maximum_value))
                                                else:
                                                    sys.stdout.write("    Max-Min:  %12.4f" % (maximum_value-minimum_value))
                                                    sys.stdout.write("    Avg:  %12.4f" % (average_value))
                                                sys.stdout.write("\n")
                                    if output_weights:
                                        sys.stdout.write("         Weights:  ")
                                        for scenario in tree_node._scenarios:
                                            sys.stdout.write("%12.4f" % scenario._w[tree_node._name][variable_id])

                                    if output_averages:
                                        sys.stdout.write("   Average:  %12.4f\n" % (average_value))

            if num_outputs_this_stage == 0:
                print("\t\tNo non-converged variables in stage")

            # cost variables aren't blended, so go through the gory computation of min/max/avg.
            # we currently always print these.
            cost_variable_name = stage._cost_variable[0]
            cost_variable_index = stage._cost_variable[1]
            print("      Cost Variable: " + cost_variable_name + indexToString(cost_variable_index))
            for tree_node in stage._tree_nodes:
                sys.stdout.write("         Tree Node: " + tree_node._name)
                if output_only_statistics is False:
                    sys.stdout.write("      (Scenarios:  ")
                    for scenario in tree_node._scenarios:
                        sys.stdout.write(scenario._name+" ")
                        if scenario == tree_node._scenarios[-1]:
                            sys.stdout.write(")\n")
                maximum_value = 0.0
                minimum_value = 0.0
                prob_sum_values = 0.0
                sum_prob = 0.0
                num_values = 0
                first_time = True
                if output_only_statistics is False:
                    sys.stdout.write("         Values:  ")
                else:
                    sys.stdout.write("         ")
                for scenario in tree_node._scenarios:
                    this_value = scenario._stage_costs[stage._name]
                    if output_only_statistics is False:
                        if this_value is not None:
                            sys.stdout.write("%12.4f" % this_value)
                        else:
                            # this is a hack, in case the stage cost variables are not returned. ipopt
                            # does this occasionally, for example, if stage cost variables are constrained
                            # to a constant value (and consequently preprocessed out).
                            sys.stdout.write("%12s" % "Not Reported")
                    if this_value is not None:
                        num_values += 1
                        prob_sum_values += scenario._probability * this_value
                        sum_prob += scenario._probability
                        if first_time:
                            first_time = False
                            maximum_value = this_value
                            minimum_value = this_value
                        else:
                            if this_value > maximum_value:
                                maximum_value = this_value
                            if this_value < minimum_value:
                                minimum_value = this_value
                    if scenario == tree_node._scenarios[-1]:
                        if num_values > 0:
                            if output_only_statistics:
                                sys.stdout.write("    Min:  %12.4f" % (minimum_value))
                                if (sum_prob > 0.0):
                                    sys.stdout.write("    Avg:  %12.4f" % (prob_sum_values/sum_prob))
                                sys.stdout.write("    Max:  %12.4f" % (maximum_value))
                            else:
                                sys.stdout.write("    Max-Min:  %12.4f" % (maximum_value-minimum_value))
                                if (sum_prob > 0.0):
                                    sys.stdout.write("   Avg:  %12.4f" % (prob_sum_values/sum_prob))
                        sys.stdout.write("\n")
