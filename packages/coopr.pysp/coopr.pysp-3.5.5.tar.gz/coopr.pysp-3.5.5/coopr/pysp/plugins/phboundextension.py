import os
import logging
import copy

import coopr.core.plugin
from coopr.pysp import phextension
from coopr.pyomo.base import minimize
from coopr.opt import UndefinedData

from operator import itemgetter
from six import iteritems

logger = logging.getLogger('coopr.pysp')

class _PHBoundBase(object):

    # Nothing interesting
    STATUS_NONE                      = 0b000
    # Used mipgap
    STATUS_MIPGAP                    = 0b001
    # Solution gap was not reported
    STATUS_GAP_NA                    = 0b010
    # Solution has nonzero
    # optimality gap
    STATUS_GAP_NONZERO               = 0b100

    WARNING_MESSAGE = {}

    # No mipgap detected, but a
    # nonzero solution gap was
    # found
    WARNING_MESSAGE[0b100] = \
        "** Possibly Conservative - Mipgap Unknown, And Nonzero Solution Gap Reported **"

    # Used mipgap and solver did
    # report a solution gap
    WARNING_MESSAGE[0b101] = \
        "** Possibly Conservative - Mipgap Detected, And Nonzero Solution Gap Reported **"

    # Used mipgap and solver did NOT
    # report a solution gap
    WARNING_MESSAGE[0b111] = \
        "** Extreme Caution - Mipgap Detected, But No Solution Gap Information Obtained - Bound May Be Invalid **"
    WARNING_MESSAGE[0b011] = \
        "** Extreme Caution - Mipgap Detected, But No Solution Gap Information Obtained - Bound May Be Invalid **"

    WARNING_MESSAGE[0b110] = \
        "** Caution - Solver Did Not Provide Solution Gap Information - Bound May Be Invalid **"
    WARNING_MESSAGE[0b010] = \
        "** Caution - Solver Did Not Provide Solution Gap Information - Bound May Be Invalid **"

    def __init__(self):

        # the interval for which bound computations
        # are performed during the ph iteration k solves.
        # A bound update is always performed at iteration 0
        # with the (non-PH-augmented) objective and the update
        # interval starts with a bound update at ph iteration 1. 
        self._update_interval = 1

        # keys are ph iteration except for the trival bound whose key
        # is None
        self._bound_history = {}
        self._status_history = {}

        self._is_minimizing = True

    #
    # Calculates the probability weighted sum of all suproblem (or
    # bundle) objective functions, assuming the most recent solution
    # corresponds to a ph solve with the weight terms active and the
    # proximal terms inactive in the objective function.
    #
    def _compute_bound(self, ph, storage_key):

        bound_status = self.STATUS_NONE
        if (ph._mipgap is not None) and (ph._mipgap > 0):
            logger.warn("A nonzero mipgap was detected when using "
                        "the PH bound plugin. The bound "
                        "computation may as a result be conservative.")
            bound_status |= self.STATUS_MIPGAP

        objective_bound = 0.0

        # If we are bundling, we compute the objective bound in a way
        # such that we can still use solution gap information if it
        # is available.
        if ph._scenario_tree.contains_bundles():

            for scenario_bundle in ph._scenario_tree._scenario_bundles:

                bundle_gap = ph._gaps[scenario_bundle._name]
                bundle_objective_value = 0.0

                for scenario in scenario_bundle._scenario_tree._scenarios:
                    # The objective must be taken from the scenario
                    # objects on PH full scenario tree
                    scenario_objective = \
                        ph._scenario_tree.get_scenario(scenario._name)._objective
                    # And we need to make sure to use the
                    # probabilities assigned to scenarios in the
                    # compressed bundle scenario tree
                    bundle_objective_value += scenario_objective * \
                                              scenario._probability

                if not isinstance(bundle_gap, UndefinedData):
                    if bundle_gap > 0:
                        bound_status |= self.STATUS_GAP_NONZERO
                        if self._is_minimizing:
                            bundle_objective_value -= bundle_gap
                        else:
                            bundle_objective_value += bundle_gap
                else:
                    bound_status |= self.STATUS_GAP_NA

                objective_bound += bundle_objective_value * \
                                   scenario_bundle._probability

        else:

            for scenario in ph._scenario_tree._scenarios:

                this_objective_value = scenario._objective
                this_gap = ph._gaps[scenario._name]

                if not isinstance(this_gap, UndefinedData):
                    if this_gap > 0:
                        bound_status |= self.STATUS_GAP_NONZERO
                        if self._is_minimizing:
                            this_objective_value -= this_gap
                        else:
                            this_objective_value += this_gap
                else:
                    bound_status |= self.STATUS_GAP_NA

                objective_bound += (scenario._probability * this_objective_value)

        print("Computed objective lower bound=%12.4f\t%s"
              % (objective_bound,
                 self.WARNING_MESSAGE.get(bound_status,"")))

        self._status_history[storage_key] = bound_status
        self._bound_history[storage_key] = objective_bound

    def report_best_bound(self):
        print("")
        best_bound = None
        if len(self._bound_history) > 0:
            if self._is_minimizing:
                best_bound_key, best_bound = max(self._bound_history.items(),
                                                 key=itemgetter(1))
            else:
                best_bound_key, best_bound = min(self._bound_history.items(),
                                                 key=itemgetter(1))
        print("Best Objective Bound: %15s\t\t%s"
              % (best_bound,
                 self.WARNING_MESSAGE.get(self._status_history[best_bound_key],"")))
        print("")
        output_filename = "phbestbound.txt"
        output_file = open(output_filename,"w")
        output_file.write("%.17g\n" % best_bound)
        output_file.close()
        print("Best Lower Bound written to file="+output_filename)

    def report_bound_history(self):
        print("")
        print("%15s %15s" % ("Iteration", "Bound"))
        output_filename = "phbound.txt"
        output_file = open(output_filename,"w")
        keys = list(self._bound_history.keys())
        if None in keys:
            keys.remove(None)
            print("%15s %15s\t\t%s"
                  % ("Trivial",
                     self._bound_history[None],
                     self.WARNING_MESSAGE.get(self._status_history[None],"")))
            output_file.write("Trivial: %.17g\n"
                              % (self._bound_history[None]))
        for key in sorted(keys):
            print("%15s %15s\t\t%s"
                  % (key,
                     self._bound_history[key],
                     self.WARNING_MESSAGE.get(self._status_history[key],"")))
            output_file.write("%d: %.17g\n"
                              % (key,
                                 self._bound_history[key]))
        print("")
        output_file.close()
        print("Lower bound history written to file="+output_filename)

class phboundextension(coopr.core.plugin.SingletonPlugin, _PHBoundBase):

    coopr.core.plugin.implements(phextension.IPHExtension)

    coopr.core.plugin.alias("phboundextension")

    def __init__(self):

        _PHBoundBase.__init__(self)

    def _iteration_k_bound_solves(self,ph, storage_key):

        # Disable the solution caching mechanism so we can restore the
        # current solution. Failing to do this would cause the cache
        # to be overwritten in the call to ph.solve_subproblems()
        ph._enable_solution_caching = False

        # snapshot the solutions on the scenarios objects in the tree
        # for restoring after we're done
        ph_solutions = dict((scenario._name, scenario.package_current_solution()) \
                            for scenario in ph._scenario_tree._scenarios)

        # Weights have not been pushed to instance parameters (or
        # transmitted to the phsolverservers) at this point
        ph._push_w_to_instances()

        # Save the current fixed state and fix queue
        ph_fixed = dict((tree_node._name, copy.deepcopy(tree_node._fixed)) \
                             for tree_node in ph._scenario_tree._tree_nodes)

        ph_fix_queue = \
            dict((tree_node._name, copy.deepcopy(tree_node._fix_queue)) \
                 for tree_node in ph._scenario_tree._tree_nodes)

        # Free all currently fixed variables
        for tree_node in ph._scenario_tree._tree_nodes:
            tree_node.clear_fix_queue()
            for variable_id in ph_fixed[tree_node._name]:
                tree_node.free_variable(variable_id)

        # Push freed variable statuses on instances (or
        # transmit to the phsolverservers)
        ph._push_fixed_to_instances()

        # the following code assumes the weight terms are already active
        # but proximal terms need to be deactivated
        if ph._drop_proximal_terms is False:
            # deactivate all proximal terms and activate all weight terms
            ph.deactivate_ph_objective_proximal_terms(transmit=True)

        # Do the preprocessing
        ph._preprocess_scenario_instances()
        
        # Disable caching of results for this set of subproblem solves
        # so we can restore the original results. we modify the scenarios
        # and re-solve - which messes up the warm-start, which can 
        # seriously impact the performance of PH. plus, we don't want lower
        # bounding to impact the primal PH in any way - it should be free
        # of any side effects.
        ph.solve_subproblems(warmstart=not ph._disable_warmstarts)

        if ph._verbose:
            print("Successfully completed PH bound extension "
                  "iteration %s solves\n"
                  "- solution statistics:\n" % (storage_key))
            if ph._scenario_tree.contains_bundles():
                ph._report_bundle_objectives()
            ph._report_scenario_objectives()

        # compute the bound
        self._compute_bound(ph,storage_key)
        
        if ph._drop_proximal_terms is False:
            # reactivate proximal terms
            ph.activate_ph_objective_proximal_terms(transmit=True)

        # restore the values of variables to their values prior to
        # invocation of this method. this will ensure that warm-starts
        # will be retained, and that the parent (primal) PH will not
        # be impacted.
        ph.restoreCachedScenarioSolutions()

        # Refix all previously fixed variables
        for tree_node in ph._scenario_tree._tree_nodes:
            for variable_id, fix_value in iteritems(ph_fixed[tree_node._name]):
                tree_node.fix_variable(variable_id, fix_value)

        # Push fixed variable statuses to instances (or
        # transmit to the phsolverservers)
        ph._push_fixed_to_instances()

        # Restore the fix_queue
        for tree_node in ph._scenario_tree._tree_nodes:
            tree_node._fix_queue.update(ph_fix_queue[tree_node._name])

        # Restore the solutions on the scenarios objects in the tree
        for scenario_name, scenario_solution in iteritems(ph_solutions):
            scenario = ph._scenario_tree.get_scenario(scenario_name)
            scenario.update_current_solution(scenario_solution)

        # Re-enable solution caching
        ph._enable_solution_caching = True

    ############ Begin Callback Functions ##############

    def pre_ph_initialization(self,ph):
        """
        Called before PH initialization.
        """
        pass

    def post_instance_creation(self, ph):
        """
        Called after PH initialization has created the scenario
        instances, but before any PH-related
        weights/variables/parameters/etc are defined!
        """
        pass

    def post_ph_initialization(self, ph):
        """
        Called after PH initialization
        """

        if ph._verbose:
            print("Invoking post initialization callback in phboundextension")

        self._is_minimizing = True if (ph._objective_sense == minimize) else False
        # TODO: Check for ph options that may not be compatible with
        #       this plugin and warn / raise exception
        
        # Enable ph's solution caching (which may be a little more
        # expensive)
        ph._enable_solution_caching = True

        # grab the update interval from the environment variable, if
        # it exists.
        update_interval_variable_name = "PHBOUNDINTERVAL"
        if update_interval_variable_name in os.environ:
            self._update_interval = int(os.environ[update_interval_variable_name])
            print("phboundextension using update interval="
                  +str(self._update_interval)+", extracted from "
                  "environment variable="+update_interval_variable_name)
        else:
            print("phboundextension using default update "
                  "interval="+str(self._update_interval))

    def post_iteration_0_solves(self, ph):
        """
        Called after the iteration 0 solves
        """

        if ph._verbose:
            print("Invoking post iteration 0 solve callback in phboundextension")

        # Always compute a lower/upper bound here because it requires
        # no work.  The instances (or bundles) have already been
        # solved with the original (non-PH-augmented) objective and
        # are loaded with results.

        #
        # Note: We will still obtain a bound using the weights
        #       computed from PH iteration 0 in the
        #       pre_iteration_k_solves callback.
        #
        ph_iter = None

        # Note: It is important that the mipgap is not adjusted
        #       between the time after the subproblem solves
        #       and before now.
        self._compute_bound(ph, ph_iter)

    def post_iteration_0(self, ph):
        """
        Called after the iteration 0 solves, averages computation, and weight computation
        """
        pass

    def pre_iteration_k_solves(self, ph):
        """
        Called immediately before the iteration k solves
        """

        #
        # Note: We invoke this callback pre iteration k in order to
        #       obtain a PH bound using weights computed from the
        #       PREVIOUS iteration's scenario solutions (including
        #       those of iteration zero).
        #
        ph_iter = ph._current_iteration-1

        if ph._verbose:
            print("Invoking pre iteration k solve callback in phboundextension")

        if (ph_iter % self._update_interval) != 0:
            return

        self._iteration_k_bound_solves(ph, ph_iter)

    def post_iteration_k_solves(self, ph):
        """
        Called after the iteration k solves!
        """
        pass

    def post_iteration_k(self, ph):
        """
        Called after the iteration k is finished, after weights have been updated!
        """
        pass

    def post_ph_execution(self, ph):
        """
        Called after PH has terminated!
        """

        if ph._verbose:
            print("Invoking post execution callback in phboundextension")

        #
        # Note: We invoke this callback in order to compute a bound
        #       using the weights obtained from the final PH
        #       iteration.
        #
        ph_iter = ph._current_iteration

        if (ph_iter % self._update_interval) == 0:

            self._iteration_k_bound_solves(ph, ph_iter)

        self.report_bound_history()
        self.report_best_bound()

