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
        Victim sends packet to each reflector according to its best path in local RIB
        """
        source_prefix = self.scenario.scenario_config.source_prefix
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
        We model two different attackers: spoofing host and spoofing AS

        Spoofing Host: attacker controls machine inside of spoofing-allowing AS, 
        the attack can send packets to reflectors according to AS's local RIB (same as victim)

        Spoofing AS: attacker controls malicious AS from which they can route spoofed packets
        to all of its neighbors with destination IP of the reflector
        """
        source_prefix = self.scenario.scenario_config.source_prefix
        origin = as_obj.asn

        # Spoofing AS model is referred to as "broadasting strategy" in code due to legacy reasons
        if self.scenario.scenario_config.attacker_broadcast:
            # broadcasting strategy
            for ann in as_obj.policy._local_rib.data.values():
                if ann.origin in self.scenario.reflector_asns:
                    dst = ann.prefix
                    for neighbor_as_obj in as_obj.neighbors:
                        # propagate packet to all neighbors with prev_hop = attacker
                        self._propagate_packet(
                            neighbor_as_obj, source_prefix, as_obj, origin, dst
                        )
        # Spoofing Host model
        else:
            # best path routing
            prev_hop = None
            for ann in as_obj.policy._local_rib.data.values():
                if ann.origin in self.scenario.reflector_asns:
                    dst = ann.prefix
                    self._propagate_packet(
                        as_obj, source_prefix, prev_hop, origin, dst
                    )

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

        outcome_int = self._data_plane_outcomes.get((as_obj.asn, source_prefix, prev_hop_asn, origin))
        # if no outcome, determine outcome
        if outcome_int is None:
            outcome_int = self._determine_as_outcome_data_plane(
                as_obj=as_obj,
                source_prefix=source_prefix,
                prev_hop=prev_hop,
                origin=origin,
                dst=dst,
                filtered=filtered,
            )
            self._data_plane_outcomes[(as_obj.asn, source_prefix, prev_hop_asn, origin)] = outcome_int
            # if packet was filtered, set flag equal to true so packets won't be revalidated later in the path
            if outcome_int in (Outcomes.FALSE_POSITIVE.value, Outcomes.TRUE_POSITIVE.value):
                filtered = True
        # if the outcome was previously determined to be filtered on path and the current packet is not filtered, 
        # revalidate the packet on said interfaces 
        elif outcome_int in (Outcomes.A_FILTERED_ON_PATH.value, Outcomes.V_FILTERED_ON_PATH.value) and not filtered:
            new_outcome_int = self._determine_as_outcome_data_plane(
                as_obj=as_obj,
                source_prefix=source_prefix,
                prev_hop=prev_hop,
                origin=origin,
                dst=dst,
                filtered=filtered,
            )
            self._data_plane_outcomes[
                (as_obj.asn, source_prefix, prev_hop_asn, origin)
            ] = min(outcome_int, new_outcome_int)
            if new_outcome_int in (Outcomes.FALSE_POSITIVE.value, Outcomes.TRUE_POSITIVE.value):
                filtered = True
        # if the packet was previously determined to be filtered, set filtered=True to prevent validating the packet later
        elif outcome_int in (Outcomes.FALSE_POSITIVE.value, Outcomes.TRUE_POSITIVE.value):
            filtered = True
        
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
        filtered: bool,
    ):
        """
        Call AS SAV policy's validation function, determine outcome
        """
        # Origins do not validate their own packets
        if as_obj.asn == origin:
            return Outcomes.ORIGIN.value

        # determine if packet is spoofed based on origin AS
        if origin in self.scenario.victim_asns:
            spoofed_packet = False
        elif origin in self.scenario.attacker_asns:
            spoofed_packet = True
        else:
            raise ValueError("Origin must be in victim_asns or attacker_asns.")

        # if packet is filtered, propagated corresponding outcome
        if filtered and spoofed_packet:
            return Outcomes.A_FILTERED_ON_PATH.value
        if filtered and not spoofed_packet:
            return Outcomes.V_FILTERED_ON_PATH.value

        sav_policy = self.scenario.sav_policy_asn_dict.get(as_obj.asn)
        if sav_policy:
            validated = sav_policy.validate(
                as_obj, source_prefix, prev_hop, self.engine, self.scenario
            )
            if validated:
                outcome = Outcomes.FALSE_NEGATIVE.value if spoofed_packet else Outcomes.TRUE_NEGATIVE.value
            elif not validated:
                outcome = Outcomes.TRUE_POSITIVE.value if spoofed_packet else Outcomes.FALSE_POSITIVE.value            
            else:
                raise ValueError("Packet did not receive an outcome?")
        # Not adopting SAV, no validation, forward packet
        else:
            outcome = Outcomes.FORWARD.value

        # connectivity check
        if outcome == Outcomes.FALSE_POSITIVE.value:
            victim_anns = set()
            for prefix_dict in as_obj.policy._ribs_in.data.values():
                for ann_info in prefix_dict.values():
                    if as_obj.policy._valid_ann(
                        ann_info.unprocessed_ann, ann_info.recv_relationship
                    ):
                        ann = ann_info.unprocessed_ann
                        if ann.origin in self.scenario.victim_asns:
                            victim_anns.add(ann)
            if source_prefix not in {ann.prefix for ann in victim_anns}:
                print(f"False Positive, disconnected.", flush=True)
                outcome = Outcomes.DISCONNECTED.value
            elif source_prefix in {ann.prefix for ann in victim_anns}:
                print(f"Validating AS: {as_obj.asn}", flush=True)
                print(f"Prev_hop: {prev_hop.asn} from {'customer' if prev_hop.asn in as_obj.customer_asns else 'peer'}", flush=True)
                print(f"Victim Anns: {victim_anns}", flush=True)

        return outcome

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
