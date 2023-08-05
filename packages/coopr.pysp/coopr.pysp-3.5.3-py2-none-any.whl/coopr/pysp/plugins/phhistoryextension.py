#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

from coopr.core.plugin import *
from coopr.pysp import phextension
from coopr.pysp.phutils import indexToString
from coopr.pysp.phsolverserverutils import TransmitType

import copy
from six import iteritems

import pickle
import shelve
import json

_USE_JSON = True

# TODO:
#   - snapshot node _fix_queue

def extract_convergence(ph):
    metric = ph._converger.lastMetric() \
             if len(ph._converger._metric_history) \
                else None
    convergence = {'metric':metric,
                   'fixed variable counts':\
                     {'continuous':ph._total_fixed_continuous_vars,
                      'discrete':ph._total_fixed_discrete_vars},
                   'blended variable counts':\
                     {'continuous':ph._total_continuous_vars,
                      'discrete':ph._total_discrete_vars}}
    return convergence

def extract_scenario_tree_structure(scenario_tree):
    scenario_tree_structure = {}
    scenario_tree_structure['scenarios'] = {}
    for scenario in scenario_tree._scenarios:
        scenario_structure = \
            scenario_tree_structure['scenarios'][scenario._name] = {}
        scenario_structure['name'] = scenario._name
        scenario_structure['probability'] = scenario._probability
        scenario_structure['nodes'] = [node._name for node in scenario._node_list]
    scenario_tree_structure['stages'] = {}
    for stage_order, stage in enumerate(scenario_tree._stages):
        stage_structure = scenario_tree_structure['stages'][stage._name] = {}
        stage_structure['name'] = stage._name
        stage_structure['nodes'] = [node._name for node in stage._tree_nodes]
        stage_structure['order'] = stage_order
    scenario_tree_structure['nodes'] = {}
    for tree_node in scenario_tree._tree_nodes:
        node_structure = scenario_tree_structure['nodes'][tree_node._name] = {}
        parent = tree_node._parent
        node_structure['name'] = tree_node._name
        node_structure['parent'] = parent._name if (parent is not None) else None
        node_structure['children'] = [child_node._name for child_node in \
                                      tree_node._children]
        node_structure['stage'] = tree_node._stage._name
        node_structure['conditional probability'] = \
            tree_node._conditional_probability
        node_structure['probability'] = tree_node._probability
        node_structure['scenarios'] = [node_scenario._name for node_scenario in \
                                       tree_node._scenarios]
    return scenario_tree_structure

def extract_scenario_solutions(scenario_tree,
                               include_ph_objective_parameters=False):
    scenario_solutions = {}
    for scenario in scenario_tree._scenarios:
        scenario_name = scenario._name
        scenario_sol = scenario_solutions[scenario_name] = {}
        variable_sol = scenario_sol['variables'] = {}
        for tree_node in scenario._node_list:
            isNotLeafNode = not tree_node.is_leaf_node()
            if isNotLeafNode and include_ph_objective_parameters:
                weight_values = scenario._w[tree_node._name]
                rho_values = scenario._rho[tree_node._name]
            x_values = scenario._x[tree_node._name]
            for variable_id, (var_name, index) in \
                  iteritems(tree_node._variable_ids):
                varsol = variable_sol[str(var_name)+str(indexToString(index))] = {}
                varsol['value'] = x_values[variable_id]
                varsol['fixed'] = scenario.is_variable_fixed(tree_node, variable_id)
                varsol['stale'] = scenario.is_variable_stale(tree_node, variable_id)

                if include_ph_objective_parameters:
                    if isNotLeafNode and \
                       (variable_id in tree_node._standard_variable_ids):
                        varsol['rho'] = rho_values[variable_id] \
                                        if (isNotLeafNode) \
                                           else None
                        varsol['weight'] = weight_values[variable_id] \
                                           if (isNotLeafNode) \
                                              else None
                    else:
                        varsol['rho'] = None
                        varsol['weight'] = None

        scenario_sol['objective'] = scenario._objective
        scenario_sol['cost'] = scenario._cost

        if include_ph_objective_parameters:
            scenario_sol['ph weight term'] = scenario._weight_term_cost
            scenario_sol['ph proximal term'] = scenario._proximal_term_cost

        scenario_sol['stage costs'] = copy.deepcopy(scenario._stage_costs)

    return scenario_solutions

def extract_node_solutions(scenario_tree,
                           include_ph_objective_parameters=False,
                           include_variable_statistics=False):
    
    scenario_tree.snapshotSolutionFromScenarios()
    node_solutions = {}
    for stage in scenario_tree._stages:
        for tree_node in stage._tree_nodes:
            isNotLeafNode = not tree_node.is_leaf_node()
            node_sol = node_solutions[tree_node._name] = {}
            variable_sol = node_sol['variables'] = {}
            for variable_id, (var_name, index) in iteritems(tree_node._variable_ids):
                sol = variable_sol[str(var_name)+str(indexToString(index))] = {}
                sol['solution'] = tree_node._solution[variable_id]
                sol['fixed'] = tree_node.is_variable_fixed(variable_id)
                sol['derived'] = bool(variable_id in tree_node._derived_variable_ids)
                if include_variable_statistics:
                    if isNotLeafNode:
                        sol['minimum'] = tree_node._minimums[variable_id]
                        sol['average'] = tree_node._averages[variable_id]
                        sol['maximum'] = tree_node._maximums[variable_id]
                    else:
                        sol['minimum'] = None
                        sol['average'] = None
                        sol['maximum'] = None
                if include_ph_objective_parameters:
                    if isNotLeafNode and \
                       (variable_id in tree_node._standard_variable_ids):
                        sol['xbar'] = tree_node._xbars[variable_id]
                        sol['wbar'] = tree_node._wbars[variable_id]
                    else:
                        sol['xbar'] = None
                        sol['wbar'] = None
            node_sol['expected cost'] = tree_node.computeExpectedNodeCost()
    return node_solutions

class phhistoryextension(SingletonPlugin):

    implements(phextension.IPHExtension)

    # the below is a hack to get this extension into the
    # set of IPHExtension objects, so it can be queried
    # automagically by PH.
    alias("PHHistoryExtension")

    def _dump_to_history(self, data, key, last=False, first=False):
        assert not (first and last)
        if _USE_JSON:
            file_string = 'wb' if first else \
                          'ab+'
            with open(self.ph_history_filename, file_string) as f:
                if first:
                    f.write('{\n')
                else:
                    # make sure we are at the end of the file
                    f.seek(0,2)
                    # overwrite the previous \n}\n
                    f.truncate(f.tell()-3)
                    f.write(',\n')
                f.write('  "'+key+'":\n')
                json.dump(data,f,indent=2)
                f.write('\n}\n')
        else:
            if first:
                flag = 'n'
            else:
                flag = 'c'
            d = shelve.open(self.ph_history_filename,
                            flag=flag,
                            protocol=pickle.HIGHEST_PROTOCOL)
            d[key] = data
            if first:
                d['results keys'] = []
            if key != 'scenario tree':
                d['results keys'] += [key]
            d.close()

    def pre_ph_initialization(self,ph):

        self.ph_history_filename = "ph_history"
        if _USE_JSON:
            self.ph_history_filename += ".json"
        else:
            self.ph_history_filename += ".db"

    def post_instance_creation(self,ph):
        pass

    def post_ph_initialization(self, ph):

        data = extract_scenario_tree_structure(ph._scenario_tree)
        self._dump_to_history(data,'scenario tree',first=True)

        # TODO: Add a print statement notifying the user of this change
        # Make sure we transmit at least all the ph variables on the
        # scenario tree (including leaf nodes). If the default
        # has already been set to transmit more, then we are fine.
        # (hence the |=)
        ph._phpyro_default_iteration_k_variable_transmission |= \
            TransmitType.all_stages
        ph._phpyro_default_iteration_k_variable_transmission |= \
            TransmitType.blended
        ph._phpyro_default_iteration_k_variable_transmission |= \
            TransmitType.derived
        ph._phpyro_default_iteration_k_variable_transmission |= \
            TransmitType.fixed
        ph._phpyro_default_iteration_k_variable_transmission |= \
            TransmitType.stale

    def post_iteration_0_solves(self, ph):
        pass

    def post_iteration_0(self, ph):
        pass

    def _snapshot_all(self, ph):
        data = {}
        data['convergence'] = extract_convergence(ph)
        data['scenario solutions'] = \
            extract_scenario_solutions(ph._scenario_tree,True)
        data['node solutions'] = \
            extract_node_solutions(ph._scenario_tree,True,True)
        return data

    def pre_iteration_k_solves(self, ph):
        key = str(ph._current_iteration - 1)
        data = self._snapshot_all(ph)
        self._dump_to_history(data,key)

    def post_iteration_k_solves(self, ph):
        pass

    def post_iteration_k(self, ph):
        pass

    def post_ph_execution(self, ph):
        key = str(ph._current_iteration)
        data = self._snapshot_all(ph)
        self._dump_to_history(data,key,last=True)

        print("PH algorithm history written to file="
              +self.ph_history_filename)

