from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy
from .efp_urpf_alg_b import EnhancedFeasiblePathuRPFAlgB
from .strict_urpf import StrictuRPF
from .loose_urpf import LooseuRPF

from bgpy.enums import ASGroups

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine
    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario

class RFC8704(BaseSAVPolicy):
    name: str = "RFC8704"

    @staticmethod
    def _validate(
        as_obj: "AS", 
        source_prefix: str, 
        prev_hop: "AS", 
        engine: "SimulationEngine", 
        scenario: "SAVScenario",
    ):
        """
        Validates packets based on security recommendations listed in RFC 8704
        
        "For a directly connected single-homed stub AS (customer), 
        the AS under consideration SHOULD perform SAV based on the strict uRPF method.
        
        For all other scenarios:    
        - The EFP-uRPF method with Algorithm B (see Section 3.4) SHOULD be applied on customer interfaces.
        - The loose uRPF method SHOULD be applied on lateral peer and transit provider interfaces."
        """
        if prev_hop.asn in engine.as_graph.asn_groups[ASGroups.STUBS.value]:
            return StrictuRPF.validate(
                as_obj, source_prefix, prev_hop, engine, scenario
            )
        elif prev_hop.asn in as_obj.customer_asns:
            return EnhancedFeasiblePathuRPFAlgB.validate(
                as_obj, source_prefix, prev_hop, engine, scenario
            )
        elif prev_hop.asn in (as_obj.peer_asns | as_obj.provider_asns):
            return LooseuRPF.validate(
                as_obj, source_prefix, prev_hop, engine, scenario
            )
        else:
            raise AssertionError("RFC8704: Should never reach this condtion.")