from typing import TYPE_CHECKING
from time import time

from bgpy.simulation_framework import BaseASGraphAnalyzer
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.enums import Plane

from sav_pkg.enums import Outcomes
from sav_pkg.simulation_framework import SAVScenario

if TYPE_CHECKING:
    from bgpy.simulation_framework.scenarios import Scenario


class SAVASGraphAnalyzer(BaseASGraphAnalyzer):
    """Performs data plane traceback, outputs outcomes"""

    def __init__(
        self,
        engine: BaseSimulationEngine,
        scenario: "Scenario",
        data_plane_tracking: bool = True,
        control_plane_tracking: bool = False,
    ) -> None:
        self.engine: BaseSimulationEngine = engine
        self.scenario: "SAVScenario" = scenario
        # data_plane_outcomes: dict[tuple, int] = {(as_obj.asn, source_prefix, prev_hop, origin): outcome}
        self._data_plane_outcomes: dict[tuple, int] = dict()
        self._control_plane_outcomes: dict[int, int] = dict()
        self.outcomes = {
            Plane.DATA.value: self._data_plane_outcomes,
            Plane.CTRL.value: self._control_plane_outcomes,
        }
        self.data_plane_tracking: bool = data_plane_tracking

    def analyze(self):
        """
        Analyzes as graph to perform data plane traceback
        """

        # if self.data_plane_tracking:
        for as_obj in self.engine.as_graph:
            if as_obj.asn in self.scenario.attacker_asns:
                self._get_attacker_outcome_data_plane(as_obj)
            elif as_obj.asn in self.scenario.victim_asns:
                self._get_victim_outcome_data_plane(as_obj)

        self._handle_outcomes()

        return self.outcomes

    def _get_victim_outcome_data_plane(self, as_obj):
        """
        Victim routes packet to reflector
        """
        source_prefix = self.scenario.scenario_config.victim_source_prefix
        origin = as_obj.asn
        prev_hop = None

        for reflector_asn in self.scenario.reflector_asns:
            self._propagate_packet(
                as_obj, source_prefix, prev_hop, origin, reflector_asn
            )

        # for reflector_asn in self.scenario.reflector_asns:
        #     for neighbor_as_obj in as_obj.neighbors:
        #         self._propagate_packet(neighbor_as_obj, source_prefix, as_obj, origin, reflector_asn)

    def _get_attacker_outcome_data_plane(self, as_obj):
        """
        For each reflector, the attacker will send a packet to each of its neighbors
        """
        source_prefix = self.scenario.scenario_config.victim_source_prefix
        origin = as_obj.asn

        for reflector_asn in self.scenario.reflector_asns:
            for neighbor_as_obj in as_obj.neighbors:
                # propagate packet to neighbor with prev_hop = attacker
                self._propagate_packet(
                    neighbor_as_obj, source_prefix, as_obj, origin, reflector_asn
                )

    def _propagate_packet(
        self, as_obj, source_prefix, prev_hop, origin, dst, filtered=False
    ):
        """
        Recursively propagates packet along AS path
        Validates packets at all ASes adopting a SAV policy
        """
        prev_hop_asn = prev_hop.asn if prev_hop is not None else None
        outcome_int = self._data_plane_outcomes.get(
            (as_obj.asn, source_prefix, prev_hop_asn, origin)
        )

        if outcome_int is None:
            outcome_int = self._determine_as_outcome_data_plane(
                as_obj, source_prefix, prev_hop, origin, filtered
            )
            self._data_plane_outcomes[
                (as_obj.asn, source_prefix, prev_hop_asn, origin)
            ] = outcome_int
        else:
            new_outcome_int = self._determine_as_outcome_data_plane(
                as_obj, source_prefix, prev_hop, origin, filtered
            )
            if outcome_int != new_outcome_int:
                # this has to do with how outcomes are enumerated
                # disconnections, forwarding, and validating packets outcomes are favored over filtering
                # this is mostly for attackers which send multiple packets
                self._data_plane_outcomes[
                    (as_obj.asn, source_prefix, prev_hop_asn, origin)
                ] = min(outcome_int, new_outcome_int)

        for ann in as_obj.policy._local_rib.data.values():
            # route by prefix (i don't think is matters for our simulations but it would still be better)
            if ann.origin == dst:
                dst_ann = ann

                # recursively propagate the packet until dst reached, packet is filtered, or the AS does not have
                # a path to the destination
                if outcome_int in [
                    Outcomes.FALSE_POSITIVE.value,
                    Outcomes.TRUE_POSITIVE.value,
                ]:
                    filtered = True

                if as_obj.asn != dst and dst_ann is not None:
                    prev_hop = as_obj
                    as_obj = self.engine.as_graph.as_dict[dst_ann.next_hop_asn]
                    self._propagate_packet(
                        as_obj, source_prefix, prev_hop, origin, dst, filtered
                    )

    def _determine_as_outcome_data_plane(
        self, as_obj, source_prefix, prev_hop, origin, filtered=False
    ):
        """
        Call AS SAV policy's validation function, determine outcome
        """

        # TODO: This seems slightly wrong in terms of enumeration and
        #       priority of certain outcomes
        if filtered:
            return Outcomes.FILTERED_ON_PATH.value
        if as_obj.asn == origin:
            return Outcomes.ORIGIN.value

        if origin in self.scenario.attacker_asns:
            spoofed_packet = True
        elif origin in self.scenario.victim_asns:
            spoofed_packet = False

        if as_obj.asn in self.scenario.sav_policy_asn_dict:
            sav_policy = self.scenario.sav_policy_asn_dict[as_obj.asn]

            validated = sav_policy.validation(
                as_obj, source_prefix, prev_hop, self.engine, self.scenario
            )
            if validated:
                return (
                    Outcomes.FALSE_NEGATIVE.value
                    if spoofed_packet
                    else Outcomes.TRUE_NEGATIVE.value
                )
            else:
                return (
                    Outcomes.TRUE_POSITIVE.value
                    if spoofed_packet
                    else Outcomes.FALSE_POSITIVE.value
                )

        # Not adopting SAV, no validation, forward packet
        else:
            return Outcomes.FORWARD.value

    def _has_outcome(self, asn, origin):
        """
        check if AS has an outcome for a given origin
        """
        for key in self._data_plane_outcomes.keys():
            if key[0] == asn and key[3] == origin:
                return True
        return False

    def _handle_outcomes(self):
        """
        Handle disconnections
        """
        # Only assign reflectors the value of disconnected
        for reflector_asn in self.scenario.reflector_asns:
            for attacker_asn in self.scenario.attacker_asns:
                if not self._has_outcome(reflector_asn, attacker_asn):
                    self._data_plane_outcomes[
                        (reflector_asn, None, None, attacker_asn)
                    ] = Outcomes.DISCONNECTED.value
            for victim_asn in self.scenario.victim_asns:
                if not self._has_outcome(reflector_asn, victim_asn):
                    self._data_plane_outcomes[
                        (reflector_asn, None, None, victim_asn)
                    ] = Outcomes.DISCONNECTED.value
