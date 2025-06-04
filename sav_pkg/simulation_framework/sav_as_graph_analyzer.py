from typing import TYPE_CHECKING

from bgpy.enums import Plane, Relationships
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_framework import BaseASGraphAnalyzer

from sav_pkg.enums import Outcomes
from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_framework.scenarios import Scenario


class SAVASGraphAnalyzer(BaseASGraphAnalyzer):
    """Performs data plane traceback, outputs outcome dict"""

    def __init__(
        self,
        engine: BaseSimulationEngine,
        scenario: "Scenario",
        data_plane_tracking: bool = True,
        control_plane_tracking: bool = False,
    ) -> None:
        self.engine: BaseSimulationEngine = engine
        self.scenario: "SAVScenario" = scenario
        # data_plane_outcomes: dict[tuple, int] = {(as_obj.asn, source_prefix, prev_hop.asn, origin.asn): outcome}
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
        print("Starting data plane analysis:", flush=True)

        for victim_asn in self.scenario.victim_asns:
            victim_as_obj = self.engine.as_graph.as_dict[victim_asn]
            self._get_victim_outcome_data_plane(victim_as_obj)
        for attacker_asn in self.scenario.attacker_asns:
            attacker_as_obj = self.engine.as_graph.as_dict[attacker_asn]
            self._get_attacker_outcome_data_plane(attacker_as_obj)

        self._handle_disconnections()

        return self.outcomes

    def _get_victim_outcome_data_plane(
        self,
        as_obj: "AS"
    ) -> None:
        """
        Victim sends packet to each reflector
        """
        source_prefix = self.scenario.scenario_config.victim_source_prefix
        origin = as_obj.asn
        prev_hop = None

        for ann in as_obj.policy._local_rib.data.values():
            if ann.origin in self.scenario.reflector_asns:
                dst = ann.prefix

                self._propagate_packet(
                    as_obj, source_prefix, prev_hop, origin, dst
                )

    def _get_attacker_outcome_data_plane(
        self,
        as_obj: "AS"
    ) -> None:
        """
        Attacker will send packets to each of its neighbors for every reflector
        This provides attacker with greater opportunity for success
        """
        source_prefix = self.scenario.scenario_config.victim_source_prefix
        origin = as_obj.asn

        for ann in as_obj.policy._local_rib.data.values():
            if ann.origin in self.scenario.reflector_asns:
                dst = ann.prefix
                for neighbor_as_obj in as_obj.neighbors:
                    # propagate packet to all neighbors with prev_hop = attacker
                    self._propagate_packet(
                        neighbor_as_obj, source_prefix, as_obj, origin, dst
                    )

                source_prefix = self.scenario.scenario_config.victim_source_prefix

        # prev_hop = None
        # for ann in as_obj.policy._local_rib.data.values():
        #     if ann.origin in self.scenario.reflector_asns:
        #         dst = ann.prefix

        #         self._propagate_packet(
        #             as_obj, source_prefix, prev_hop, origin, dst
        #         )

    def _propagate_packet(
        self,
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        origin: int,
        dst: str,
        filtered: bool = False
    ):
        """
        Recursively propagates packet along AS path
        Validates packets at all ASes adopting a SAV policy
        """
        prev_hop_asn = prev_hop.asn if prev_hop is not None else None

        if filtered and self._data_plane_outcomes.get((as_obj.asn, source_prefix, prev_hop_asn, origin)) is None:
            if origin in self.scenario.victim_asns:
                self._data_plane_outcomes[
                    (as_obj.asn, source_prefix, prev_hop_asn, origin)
                ] = Outcomes.V_FILTERED_ON_PATH.value
            elif origin in self.scenario.attacker_asns:
                self._data_plane_outcomes[
                    (as_obj.asn, source_prefix, prev_hop_asn, origin)
                ] = Outcomes.A_FILTERED_ON_PATH.value
        else:
            # check if outcome was previously determined
            outcome_int = self._data_plane_outcomes.get((as_obj.asn, source_prefix, prev_hop_asn, origin))

            if outcome_int is None:
                outcome_int = self._determine_as_outcome_data_plane(
                    as_obj, source_prefix, prev_hop, origin, filtered
                )
                self._data_plane_outcomes[(as_obj.asn, source_prefix, prev_hop_asn, origin)] = outcome_int

                if outcome_int in (Outcomes.FALSE_POSITIVE.value, Outcomes.TRUE_POSITIVE.value):
                    # If the packet was invalidated & filtered, we will propagate the remaining path
                    # assigning each remaining AS the outcome filtered_on_path
                    filtered = True

            elif outcome_int in [Outcomes.V_FILTERED_ON_PATH.value, Outcomes.A_FILTERED_ON_PATH.value]:
                new_outcome_int = self._determine_as_outcome_data_plane(
                    as_obj, source_prefix, prev_hop, origin, filtered
                )
                # We use the min of the two outcomes due to how outcomes are enumerated
                # filtered_on_path > all other outcomes
                self._data_plane_outcomes[
                    (as_obj.asn, source_prefix, prev_hop_asn, origin)
                ] = min(outcome_int, new_outcome_int)

        # route packet to dst
        dst_ann = as_obj.policy._local_rib.get(dst)
        if dst_ann and (dst_ann.recv_relationship.value != Relationships.ORIGIN.value):
            prev_hop = as_obj
            as_obj = self.engine.as_graph.as_dict[dst_ann.next_hop_asn]
            self._propagate_packet(
                as_obj, source_prefix, prev_hop, origin, dst, filtered
            )

    def _determine_as_outcome_data_plane(
        self,
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        origin: int,
        dst: str,
        filtered: bool = False
    ):
        """
        Call AS SAV policy's validation function, determine outcome
        """

        # Origins do not validate their own packets
        if as_obj.asn == origin:
            return Outcomes.ORIGIN.value

        if origin in self.scenario.victim_asns:
            spoofed_packet = False
        elif origin in self.scenario.attacker_asns:
            spoofed_packet = True
        else:
            raise ValueError("Origin must be in victim_asns or attacker_asns.")

        sav_policy = self.scenario.sav_policy_asn_dict.get(as_obj.asn)
        if sav_policy:
            validated = sav_policy.validate(
                as_obj, source_prefix, prev_hop, self.engine, self.scenario
            )
            if validated:
                return (
                    Outcomes.FALSE_NEGATIVE.value
                    if spoofed_packet
                    else Outcomes.TRUE_NEGATIVE.value
                )
            elif not validated:
                return (
                    Outcomes.TRUE_POSITIVE.value
                    if spoofed_packet
                    else Outcomes.FALSE_POSITIVE.value
                )
            else:
                raise ValueError("Packet did not receive an outcome?")
        # Not adopting SAV, no validation, forward packet
        else:
            return Outcomes.FORWARD.value

    def _has_outcome(
        self,
        asn: int,
        origin: int
    ) -> bool:
        """
        check if AS has an outcome for a given origin
        """
        return any(asn == key[0] and origin == key[3] for key in self._data_plane_outcomes)

    def _has_ann(
        self,
        asn: int,
        origin: int
    ) -> bool:
        as_obj = self.engine.as_graph.as_dict[asn]
        for ann in as_obj.policy._local_rib.data.values():
            if ann.origin == origin:
                return True
        return False

    def _handle_disconnections(self):
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
                    assert not self._has_ann(attacker_asn, reflector_asn)
            for victim_asn in self.scenario.victim_asns:
                if not self._has_outcome(reflector_asn, victim_asn):
                    self._data_plane_outcomes[
                        (reflector_asn, None, None, victim_asn)
                    ] = Outcomes.DISCONNECTED.value
                    assert not self._has_ann(victim_asn, reflector_asn)
