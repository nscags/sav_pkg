from typing import Optional, TYPE_CHECKING

from bgpy.simulation_framework import BaseASGraphAnalyzer
from bgpy.as_graphs import AS
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.enums import Plane

from sav_pkg.enums import Outcomes

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_framework.scenarios import Scenario


class SAVASGraphAnalyzer(BaseASGraphAnalyzer):
    
    def __init__(
        self,
        engine: BaseSimulationEngine,
        scenario: "Scenario",
        data_plane_tracking: bool = True,
        control_plane_tracking: bool = False,
    ) -> None:
        self.engine: BaseSimulationEngine = engine
        self.scenario: "Scenario" = scenario
        self._data_plane_outcomes = dict(dict(dict()))
        self._control_plane_outcomes: dict[int, int] = dict()
        self.outcomes = {
            Plane.DATA.value: self._data_plane_outcomes,
            Plane.CTRL.value: self._control_plane_outcomes,
        }
        self.data_plane_tracking: bool = data_plane_tracking


    def analyze(self):
        """
        data plane analysis -> outcomes
        """

        if self.data_plane_tracking:
            for as_obj in self.engine.as_graph:
                if as_obj.asn in self.scenario.attacker_asns:
                    self._get_attacker_outcome_data_plane(as_obj)
                elif as_obj.asn in self.scenario.victim_asns:
                    self._get_victim_outcome_data_plane(as_obj)
                
        # determine disconnections after all packets are sent
        self._handle_outcomes()

        return self.outcomes
    

    def _get_victim_outcome_data_plane(self, as_obj):
        # as_obj is the victim
        origin = as_obj.asn
        prev_hop = None

        for reflector_asn in self.scenario.reflector_asns:
            self._propagate_packet(as_obj, reflector_asn, origin, prev_hop)
    

    def _get_attacker_outcome_data_plane(self, as_obj):
        # as_obj is the attacker
        origin = as_obj.asn

        for reflector_asn in self.scenario.reflector_asns:
            for neighbor_as_obj in as_obj.neighbors:
                # propagate packet to neighbor with prev_hop = attacker
                self._propagate_packet(neighbor_as_obj, reflector_asn, origin, as_obj)


    def _propagate_packet(self, as_obj, dst, origin, prev_hop):
        if (
            # AS in outcome dict
            as_obj.asn in self._data_plane_outcomes and
            # Attacker/victim packet already in dict
            origin in self._data_plane_outcomes[as_obj.asn] and
            # Outcome for specific interface in dict
            self._data_plane_outcomes[as_obj.asn][origin].get(prev_hop.asn if prev_hop is not None else None) is not None
        ):
            outcome_int = self._data_plane_outcomes[as_obj.asn][origin][prev_hop.asn if prev_hop is not None else None]
        else:
            # determine outcome
            outcome_int = self._determine_as_outcome_data_plane(as_obj, prev_hop, origin)

            # add outcome to nested dict
            # {asn: {origin: {prev_hop: outcome}}}
            if as_obj.asn not in self._data_plane_outcomes:
                self._data_plane_outcomes[as_obj.asn] = {}

            if origin not in self._data_plane_outcomes[as_obj.asn]:
                self._data_plane_outcomes[as_obj.asn][origin] = {}

            self._data_plane_outcomes[as_obj.asn][origin][prev_hop.asn if prev_hop is not None else None] = outcome_int

        # look through local_rib for announcement to dst
        for ann in as_obj.policy._local_rib.data.values():
            if ann.as_path[-1] == dst:
                dst_ann = ann

                # recursively propagate the packet until dst reached, packet is filtered, or the AS does not have
                # a path to the destination
                if (outcome_int not in [Outcomes.FALSE_POSITIVE.value, Outcomes.TRUE_POSITIVE.value] 
                    and as_obj.asn != dst 
                    and dst_ann is not None):
                    prev_hop = as_obj
                    as_obj = self.engine.as_graph.as_dict[dst_ann.next_hop_asn]
                    self._propagate_packet(as_obj, dst, origin, prev_hop)


    def _determine_as_outcome_data_plane(self, as_obj, prev_hop, origin):
        # Attacker and Victim don't validate their own packets

        # NOTE: Though this is fine for attacker/victim at the edge
        #       if the attacker were to fall on the route between the
        #       victim and reflector, this will cause errors
        # TODO: Change this eventually so the attackers and victims
        #       will perform SAV if as_obj.asn != origin
        if as_obj.asn in self.scenario.attacker_asns:
            return Outcomes.ATTACKER.value
        elif as_obj.asn in self.scenario.victim_asns:
            return Outcomes.VICTIM.value

        if origin in self.scenario.attacker_asns:
            spoofed_packet = True
        elif origin in self.scenario.victim_asns:
            spoofed_packet = False

        # look for ASN in dict and validate using SAV policy
        if as_obj.asn in self.scenario.sav_policy_asn_dict:
            sav_policy = self.scenario.sav_policy_asn_dict[as_obj.asn]
            
            # determine if packet is validated
            validated = sav_policy.validate(as_obj, prev_hop, origin, self.engine)
            if validated and spoofed_packet:
                return Outcomes.FALSE_NEGATIVE.value
            elif validated and not spoofed_packet:
                return Outcomes.TRUE_NEGATIVE.value
            elif not validated and spoofed_packet:
                return Outcomes.TRUE_POSITIVE.value
            elif not validated and not spoofed_packet:
                return Outcomes.FALSE_POSITIVE.value
        # Not adopting SAV, no validation, forward packet
        else:
            if spoofed_packet:
                return Outcomes.FALSE_NEGATIVE.value
            elif not spoofed_packet:
                return Outcomes.TRUE_NEGATIVE.value


    def _handle_outcomes(self):
        # go through as graph
        for as_obj in self.engine.as_graph:
            # ASes with outcome = None are disconnected
            if as_obj.asn in self._data_plane_outcomes:
                for origin, prev_hops in self._data_plane_outcomes[as_obj.asn].items():
                    for prev_hop, outcome in prev_hops.items():
                        if outcome is None:
                            self._data_plane_outcomes[as_obj.asn][origin][prev_hop] = Outcomes.DISCONNECTED.value
            # ASes without an entry in the dict are also disconnected
            else:
                for victim_asn in self.scenario.victim_asns:
                    self._data_plane_outcomes[as_obj.asn] = {victim_asn: {-1: Outcomes.DISCONNECTED.value}}
                for attacker_asn in self.scenario.attacker_asns:
                    self._data_plane_outcomes[as_obj.asn] = {attacker_asn: {-1: Outcomes.DISCONNECTED.value}}