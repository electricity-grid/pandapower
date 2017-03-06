# -*- coding: utf-8 -*-

# Copyright (c) 2016 by University of Kassel and Fraunhofer Institute for Wind Energy and Energy
# System Technology (IWES), Kassel. All rights reserved. Use of this source code is governed by a
# BSD-style license that can be found in the LICENSE file.

import numpy as np
import copy
from numpy import ones, arange
from pandapower.results_branch import _get_branch_results
from pandapower.results_gen import _get_gen_results
from pandapower.results_bus import _get_bus_results, _get_p_q_results, _set_buses_out_of_service, \
                                   _get_shunt_results, _get_p_q_results_opf

def _extract_results(net, ppc, trafo_loading, ac=True):
    _set_buses_out_of_service(ppc)
    # generate bus_lookup net -> consecutive ordering
    maxBus = max(net["bus"].index.values)
    bus_lookup_aranged = -np.ones(maxBus + 1, dtype=int)
    bus_lookup_aranged[net["bus"].index.values] = np.arange(len(net["bus"].index.values))

    bus_pq = _get_p_q_results(net, bus_lookup_aranged, ac)
    _get_shunt_results(net, ppc, bus_lookup_aranged, bus_pq, ac)
    _get_branch_results(net, ppc, bus_lookup_aranged, bus_pq, trafo_loading, ac)
    _get_gen_results(net, ppc, bus_lookup_aranged, bus_pq, ac)
    _get_bus_results(net, ppc, bus_pq, ac)

def _extract_results_opf(net, ppc, trafo_loading, ac):
    # generate bus_lookup net -> consecutive ordering
    maxBus = max(net["bus"].index.values)
    bus_lookup_aranged = -ones(maxBus + 1, dtype=int)
    bus_lookup_aranged[net["bus"].index.values] = arange(len(net["bus"].index.values))

    _set_buses_out_of_service(ppc)
    bus_pq = _get_p_q_results_opf(net, ppc, bus_lookup_aranged)
    _get_shunt_results(net, ppc, bus_lookup_aranged, bus_pq, ac)
    _get_branch_results(net, ppc, bus_lookup_aranged, bus_pq, trafo_loading, ac)
    _get_gen_results(net, ppc, bus_lookup_aranged, bus_pq, ac)
    _get_bus_results(net, ppc, bus_pq, ac)
    _get_costs(net, ppc)

def _get_costs(net, ppc):
    net.res_cost = ppc['obj']


def reset_results(net):
    net["res_bus"] = copy.copy(net["_empty_res_bus"])
    net["res_ext_grid"] = copy.copy(net["_empty_res_ext_grid"])
    net["res_line"] = copy.copy(net["_empty_res_line"])
    net["res_load"] = copy.copy(net["_empty_res_load"])
    net["res_sgen"] = copy.copy(net["_empty_res_sgen"])
    net["res_trafo"] = copy.copy(net["_empty_res_trafo"])
    net["res_trafo3w"] = copy.copy(net["_empty_res_trafo3w"])
    net["res_shunt"] = copy.copy(net["_empty_res_shunt"])
    net["res_impedance"] = copy.copy(net["_empty_res_impedance"])
    net["res_gen"] = copy.copy(net["_empty_res_gen"])
    net["res_ward"] = copy.copy(net["_empty_res_ward"])
    net["res_xward"] = copy.copy(net["_empty_res_xward"])
    net["res_dcline"] = copy.copy(net["_empty_res_dcline"])
    
def _copy_results_ppci_to_ppc(result, ppc, opf = False):
    '''
    result contains results for all in service elements
    ppc shall get the results for in- and out of service elements
    -> results must be copied

    ppc and ppci are structured as follows:

          [in_service elements]
    ppc = [out_of_service elements]

    result = [in_service elements]

    @author: fschaefer

    @param result:
    @param ppc:
    @return:
    '''

    # copy the results for bus, gen and branch
    # busses are sorted (REF, PV, PQ, NONE) -> results are the first 3 types
    n_cols = np.shape(ppc['bus'])[1]
    ppc['bus'][:len(result['bus']), :n_cols] = result['bus'][:len(result['bus']), :n_cols]
    # in service branches and gens are taken from 'internal'
    n_cols = np.shape(ppc['branch'])[1]
    ppc['branch'][result["internal"]['branch_is'], :n_cols] = result['branch'][:, :n_cols]
    n_cols = np.shape(ppc['gen'])[1]
    ppc['gen'][result["internal"]['gen_is'], :n_cols] = result['gen'][:, :n_cols]
    ppc['internal'] = result['internal']

    ppc['success'] = result['success']
    ppc['et'] = result['et']

    if opf:
        ppc['obj'] = result['f']
        ppc['internal_gencost'] = result['gencost']

    result = ppc
    return result
