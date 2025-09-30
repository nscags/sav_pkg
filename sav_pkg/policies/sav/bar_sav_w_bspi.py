from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy
from .bar_sav import BAR_SAV
from .bar_sav_pi import BAR_SAV_PI

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine

    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario


class BAR_SAV_wBSPI(BaseSAVPolicy):
    name: str = "BAR-SAV w/ BSPI"

    @staticmethod
    def _validate( 
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ):
        if prev_hop.asn in (as_obj.customer_asns | as_obj.peer_asns):
            return BAR_SAV._validate(
                as_obj=as_obj,
                source_prefix=source_prefix,
                prev_hop=prev_hop,
                engine=engine,
                scenario=scenario
            )
        elif prev_hop.asn in as_obj.provider_asns:
            return BAR_SAV_PI._validate(
                as_obj=as_obj,
                source_prefix=source_prefix,
                prev_hop=prev_hop,
                engine=engine,
                scenario=scenario
            )
        else:
            raise ValueError("prev_hop not in customer, peers, or providers?")