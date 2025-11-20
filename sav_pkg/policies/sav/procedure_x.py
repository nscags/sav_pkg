from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy
from sav_pkg.enums import Interfaces
import ipaddress

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine
    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario


class ProcedureX(BaseSAVPolicy):
    """
    Simple SAV procedure:

    - Applied only on CUSTOMER + PEER interfaces.
    - Accept the packet only if the AS has seen ANY valid announcement
      for the source prefix from the prev_hop in RIBs-In.
    """
    name: str = "Procedure X"
    applied_interfaces = frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value])

    @staticmethod
    def _validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hhop: "AS",
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ) -> bool:
        # Convert prefix to network object
        src = ipaddress.ip_network(source_prefix)

        # Look only at announcements from prev_hop AS in RIBs-In
        rib_dict = as_obj.policy._ribs_in.data.get(prev_hhop.asn, {})

        for prefix, ann_info in rib_dict.items():
            ann_prefix = ipaddress.ip_network(ann_info.unprocessed_ann.prefix)

            # If the source prefix is part of any prefix coming from prev_hop → allowed
            if src.subnet_of(ann_prefix):
                return True

        # No matching prefix found → reject
        return False
