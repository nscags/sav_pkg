from frozendict import frozendict
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sav_pkg.enums import Interfaces

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine
    

class BaseSAVPolicy(ABC):
    name: str = "No SAV"

    @staticmethod
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
        sav_policy = scenario.sav_policy_asn_dict[as_obj.asn]
        applied_interfaces = get_applied_interfaces(as_obj, scenario, sav_policy)

        if any(prev_hop.asn in subset for subset in applied_interfaces):
            return sav_policy._validate(
                as_obj,
                source_prefix,
                prev_hop,
                engine,
                scenario,
            )
        else:
            return True

    @staticmethod
    @abstractmethod
    def _validate(self, *args, **kwargs) -> bool:
        """
        Performs validation policy on packet
        """
        pass


DEFAULT_SAV_POLICY_INTERFACE_DICT: frozendict[str, frozenset] = frozendict({
    "No SAV": frozenset(),
    "Loose uRPF": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "Strict uRPF": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
    "Feasible-Path uRPF": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "EFP uRPF Alg A": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
    "EFP uRPF Alg A wo Peers": frozenset([Interfaces.CUSTOMER.value]),
    "EFP uRPF Alg B": frozenset([Interfaces.CUSTOMER.value]),
    "RFC8704": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "Refined Alg A": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
    "BAR-SAV PI": frozenset([Interfaces.PROVIDER.value]),
    "BAR-SAV Full": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value, Interfaces.PROVIDER.value]),
    "Procedure X": frozenset([Interfaces.CUSTOMER.value, Interfaces.PEER.value]),
})

def get_applied_interfaces(
    as_obj: "AS",
    scenario,
    sav_policy
):
    """Gets the applied interfaces based on the given SAV policy."""

    interfaces = (
        scenario.scenario_config.override_default_interface_dict.get(sav_policy.name)
        if scenario.scenario_config.override_default_interface_dict
        else DEFAULT_SAV_POLICY_INTERFACE_DICT[sav_policy.name]
    )

    interface_map = {
        Interfaces.CUSTOMER.value: as_obj.customer_asns,
        Interfaces.PEER.value: as_obj.peer_asns,
        Interfaces.PROVIDER.value: as_obj.provider_asns,
    }

    applied_interfaces = {interface_map[i] for i in interfaces if i in interface_map}

    return applied_interfaces