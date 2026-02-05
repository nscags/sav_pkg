from .fp_urpf import FeasiblePathuRPF

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine


class FeasiblePathuRPF_OTC(FeasiblePathuRPF):

    @staticmethod
    def validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario,
    ) -> bool:
        # This version of FP-uRPF is applied to only customer interfaces
        if prev_hop.asn not in as_obj.customer_asns:
            return True 
        else:
            return FeasiblePathuRPF._validate(as_obj, source_prefix, prev_hop, engine, scenario)
