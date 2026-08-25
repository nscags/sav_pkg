from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy
from .bar_sav_pp import BAR_SAV_PP
from .bar_sav_pi_pp_alg_b import BAR_SAV_PI_PP_Alg_B

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine

    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario


class BAR_SAV_PP_wBSPI_PP_Alg_B(BaseSAVPolicy):
    name: str = "BAR-SAV++ w/ BSPI++ Algorithm B"

    def validate(
        self,
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario,
    ) -> bool:
        """
        BAR-SAV++ w/BSPI++ Algorithm B defines BAR-SAV++ for customer and bilateral peer interfaces 
        and BAR-SAV-PI++ Algorithm B for provider interfaces
        """
        return BAR_SAV_PP_wBSPI_PP_Alg_B._validate(as_obj, source_prefix, prev_hop, engine, scenario)

    @staticmethod
    def _validate( 
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ):
        if prev_hop.asn in (as_obj.customer_asns | as_obj.peer_asns):
            return BAR_SAV_PP._validate(
                as_obj=as_obj,
                source_prefix=source_prefix,
                prev_hop=prev_hop,
                engine=engine,
                scenario=scenario
            )
        elif prev_hop.asn in as_obj.provider_asns:
            return BAR_SAV_PI_PP_Alg_B._validate(
                as_obj=as_obj,
                source_prefix=source_prefix,
                prev_hop=prev_hop,
                engine=engine,
                scenario=scenario
            )
        else:
            raise ValueError("prev_hop not in customer, peers, or providers?")