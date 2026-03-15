from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine

    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario


class ProcedureX(BaseSAVPolicy):
    name: str = "Procedure X"

    def validate(
        self,
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario,
    ) -> bool:
        return ProcedureX._validate(as_obj, source_prefix, prev_hop, engine, scenario)

    @staticmethod
    def _validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ):
        raise NotImplementedError
