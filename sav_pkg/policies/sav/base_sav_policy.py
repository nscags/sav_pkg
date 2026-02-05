from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine


class BaseSAVPolicy(ABC):
    name: str = "No SAV"

    @staticmethod
    @abstractmethod
    def validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario,
    ) -> bool:
        """
        Applies SAV policy to specificed interfaces.
        """
        pass

    @staticmethod
    @abstractmethod
    def _validate(self, *args, **kwargs) -> bool:
        """
        Performs validation policy on packet
        """
        pass
