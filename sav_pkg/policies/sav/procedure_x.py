import ipaddress
from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy
from bgpy.simulation_engine import ASPA

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine
    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario


class ProcedureX(BaseSAVPolicy):
    name: str = "Procedure X"

    @staticmethod
    def _get_p_set(
            as_obj: "AS",
            prev_hop: "AS",
            engine: "SimulationEngine",
            scenario: "SAVScenario",
    ):
        """
        Implements Procedure X from BAR‑SAV draft §3, using ASPA and ROA only:

        Step A: Compute AS-set A = customer cone of AS-k (prev_hop ASN)
        Step B: Compute P‑set: prefixes in ROAs whose origin ASN is in AS-set A
        """
        customer_cone = set()
        # Step A.1: Initialize: S(1) = {AS‑k}
        s = {prev_hop.asn}
        i = 1

        visited = set()
        while True:
            visited |= s
            # Step A.4: S(i+1) = all ASNs whose ASPA data declares at least one
            # in S(i) as a Provider
            next_s = set()
            for asn in s:
                as_node = engine.as_graph.as_dict.get(asn)
                if not as_node:
                    continue
                for customer_asn in as_node.customer_asns:
                    cust = engine.as_graph.as_dict.get(customer_asn)
                    if cust and isinstance(cust.policy, ASPA):
                        # ASPA data shows cust uses asn as provider
                        next_s.add(customer_asn)
            i += 1
            if not next_s:
                break
            s = next_s - visited

        # Step A.6: A = union of all S(i)
        customer_cone = visited

        # Step B.7: collect prefixes from ROAs where origin ∈ customer_cone
        p_set = set()
        for roa in scenario.roa_infos:
            if roa.origin in customer_cone:
                p_set.add(str(ipaddress.ip_network(roa.prefix)))

        return customer_cone, p_set

    @staticmethod
    def _validate(
            as_obj: "AS",
            source_prefix: str,
            prev_hop: "AS",
            engine: "SimulationEngine",
            scenario: "SAVScenario",
    ):
        """
        Returns True if source_prefix is in P‑set for interface with prev_hop (AS‑k)
        else False.
        """
        _, p_set = ProcedureX._get_p_set(
            as_obj=as_obj,
            prev_hop=prev_hop,
            engine=engine,
            scenario=scenario,
        )
        src = ipaddress.ip_network(source_prefix)
        return any(src.subnet_of(ipaddress.ip_network(prefix)) for prefix in p_set)

## old code:
# from typing import TYPE_CHECKING
#
# from .base_sav_policy import BaseSAVPolicy
#
# if TYPE_CHECKING:
#     from bgpy.as_graphs.base import AS
#     from bgpy.simulation_engine import SimulationEngine
#
#     from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario
#
#
# class ProcedureX(BaseSAVPolicy):
#     name: str = "Procedure X"
#
#     @staticmethod
#     def _validate(
#         as_obj: "AS",
#         source_prefix: str,
#         prev_hop: "AS",
#         engine: "SimulationEngine",
#         scenario: "SAVScenario",
#     ):
#         raise NotImplementedError
