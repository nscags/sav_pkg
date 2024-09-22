from typing import Optional, TYPE_CHECKING

from bgpy.simulation_framework import ASGraphAnalyzer
from bgpy.as_graphs import AS
from bgpy.simulation_engine import BaseSimulationEngine

from sav_pkg.enums import Outcomes, Plane, Relationships, ASNs

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_framework.scenarios import Scenario


class SAVASGraphAnalyzer(ASGraphAnalyzer):
    """Takes in a BaseSimulationEngine and outputs metrics"""

    def __init__(
        self,
        engine: BaseSimulationEngine,
        scenario: "Scenario",
        data_plane_tracking: bool = True,
        control_plane_tracking: bool = False,
    ) -> None:
        self.engine: BaseSimulationEngine = engine
        self.scenario: "Scenario" = scenario
        # self._reflector_ann_dict: dict[AS, Optional["Ann"]] = {
        #     # Get the most specific ann in the rib
        #     as_obj: self._get_reflector_ann(as_obj)
        #     for as_obj in engine.as_graph
        # }
        self._attacker_data_plane_outcomes: dict[int, int] = dict()
        self._victim_data_plane_outcomes: dict[int, int] = dict()
        self._data_plane_outcomes: dict[int, int] = dict()
        self._control_plane_outcomes: dict[int, int] = dict()
        self.outcomes = {
            Plane.DATA.value: self._data_plane_outcomes,
            Plane.CTRL.value: self._control_plane_outcomes,
        }
        self.data_plane_tracking: bool = data_plane_tracking

    def analyze(self) -> dict[int, dict[int, int]]:
        """
        data plane analysis -> outcomes
        """

        for as_obj in self.engine.as_graph:
            if (as_obj.asn in self.scenario.attacker_asns or 
                as_obj.asn in self.scenario.victim_asns):
                if self.data_plane_tracking:
                    self._get_as_outcome_data_plane(as_obj, self.engine)
                self._get_other_as_outcome_hook(as_obj)

        # handle combining outcome dicts
        self._handle_outcomes()

        return self.outcomes
                   
    ####################
    # Data plane funcs #
    ####################


    def _propagate_packet():
        pass


    def _get_as_outcome_data_plane(self, as_obj: AS, engine) -> int:
        """
        Traceback from attacker->reflector and vitcim->reflector
        """

        # for neighbor in as_obj.neighbors:
        #     pass

        # local_rib first if that fails iterate though neighbor?
        # break if you reach the reflector?
        # this would show multiple paths
        # what if all paths fail? 
        # I guess we could show that on the graph as well

        if as_obj.asn in self.scenario.attacker_asns:
            for ann in as_obj.policy._local_rib.data.values():
                # ann is for specific as_obj
                if ann.as_path[-1] in self.scenario.reflector_asns:
                    dst = ann.as_path[-1]
                    tmp_as_obj = as_obj
                    prev_hop = None
                    as_path = [tmp_as_obj]

                    while True:
                        # Get announcement for dst at each AS along path
                        for ann_ in tmp_as_obj.policy._local_rib.data.values():
                            if ann_.as_path[-1] == dst:
                                tmp_ann = ann_

                        # Outcome already in dict
                        if self._attacker_data_plane_outcomes.get(tmp_as_obj.asn):
                            # spoofed packet filtered
                            if self._attacker_data_plane_outcomes[tmp_as_obj.asn] == Outcomes.TRUE_POSITIVE.value:
                                break
                            # spoofed packet forwarded
                            else:
                                if tmp_as_obj.asn == dst:
                                    break
                                else:
                                    prev_hop = tmp_as_obj
                                    tmp_as_obj = self.engine.as_graph.as_dict[tmp_ann.next_hop_asn]
                                    as_path.insert(0, tmp_as_obj)
                        # Outcome not in outcome dict
                        else:
                            spoofed_packet = True
                            outcome_int = self._determine_as_outcome_data_plane(tmp_as_obj, 
                                                                                tmp_ann, 
                                                                                spoofed_packet, 
                                                                                prev_hop,
                                                                                engine,
                                                                                as_path)
                            self._attacker_data_plane_outcomes[tmp_as_obj.asn] = outcome_int
                            if tmp_as_obj.asn == dst:
                                break
                            else:
                                prev_hop = tmp_as_obj
                                tmp_as_obj = self.engine.as_graph.as_dict[tmp_ann.next_hop_asn]
                                as_path.insert(0, tmp_as_obj)  

        elif as_obj.asn in self.scenario.victim_asns:
            for ann in as_obj.policy._local_rib.data.values():
                # ann is for specific as_obj
                if ann.as_path[-1] in self.scenario.reflector_asns:
                    dst = ann.as_path[-1]
                    tmp_as_obj = as_obj
                    prev_hop = None
                    as_path = [tmp_as_obj]

                    while True:
                        # Get announcement for dst at each AS along path
                        for ann_ in tmp_as_obj.policy._local_rib.data.values():
                            if ann_.as_path[-1] == dst:
                                tmp_ann = ann_
                        
                        # Outcome already in dict
                        if self._victim_data_plane_outcomes.get(tmp_as_obj.asn):
                            # legitimate packet filtered
                            if self._victim_data_plane_outcomes[tmp_as_obj.asn] == Outcomes.FALSE_POSITIVE.value:
                                break
                            # legitimate packet forwarded
                            else: 
                                if tmp_as_obj.asn == dst:
                                    break
                                else:
                                    prev_hop = tmp_as_obj
                                    tmp_as_obj = self.engine.as_graph.as_dict[tmp_ann.next_hop_asn]
                                    as_path.insert(0, tmp_as_obj)
                        # Outcome not in dict
                        else:
                            spoofed_packet = False
                            outcome_int = self._determine_as_outcome_data_plane(tmp_as_obj, 
                                                                                tmp_ann, 
                                                                                spoofed_packet, 
                                                                                prev_hop, 
                                                                                engine,
                                                                                as_path)
                            self._victim_data_plane_outcomes[tmp_as_obj.asn] = outcome_int
                            if tmp_as_obj.asn == dst:
                                break
                            else:
                                prev_hop = tmp_as_obj
                                tmp_as_obj = self.engine.as_graph.as_dict[tmp_ann.next_hop_asn]
                                as_path.insert(0, tmp_as_obj) 
                            
    def _determine_as_outcome_data_plane(
        self, 
        as_obj: AS, 
        ann: Optional["Ann"], 
        spoofed_packet, 
        prev_hop,
        engine,
        as_path
    ) -> int:
        """
        Check if as_obj is deploying SAV
        if yes:
          run SAV policy and determine outcome
        if no:
          forward packet to next AS
        """ 

        # Attacker and Victim ASes do not perform SAV for packet they are sending
        if as_obj.asn in self.scenario.attacker_asns:
            return Outcomes.ATTACKER.value
        elif as_obj.asn in self.scenario.victim_asns:
            return Outcomes.VICTIM.value
        
        # ASes deploying SAV
        elif as_obj.policy.source_address_validation_policy is not None:
            validated = as_obj.policy.source_address_validation_policy.validate(as_obj=as_obj, 
                                                                                prev_hop=prev_hop,
                                                                                engine=engine,
                                                                                as_path=as_path
                                                                                )
            if validated and spoofed_packet:
                return Outcomes.FALSE_NEGATIVE.value
            elif validated and not spoofed_packet:
                return Outcomes.TRUE_NEGATIVE.value
            elif not validated and spoofed_packet:
                return Outcomes.TRUE_POSITIVE.value
            elif not validated and not spoofed_packet:
                return Outcomes.FALSE_POSITIVE.value
            
        # ASes along path not deploying SAV
        else:
            if spoofed_packet:
                return Outcomes.FALSE_NEGATIVE.value
                # return Outcomes.ON_ATTACKER_PATH.value
            elif not spoofed_packet:
                return Outcomes.TRUE_NEGATIVE.value
                # return Outcomes.ON_VICTIM_PATH.value

    def _handle_outcomes(self):
        for as_obj in self.engine.as_graph:
            # ASes without outcomes were disconnected
            if self._attacker_data_plane_outcomes.get(as_obj.asn) is None:
                self._attacker_data_plane_outcomes[as_obj.asn] = Outcomes.DISCONNECTED.value
            if self._victim_data_plane_outcomes.get(as_obj.asn) is None:
                self._victim_data_plane_outcomes[as_obj.asn] = Outcomes.DISCONNECTED.value
            
            attacker_outcome = self._attacker_data_plane_outcomes[as_obj.asn]
            victim_outcome = self._victim_data_plane_outcomes[as_obj.asn]

            if (attacker_outcome == Outcomes.DISCONNECTED.value and
                victim_outcome == Outcomes.DISCONNECTED.value):
                self._data_plane_outcomes[as_obj.asn] = Outcomes.DISCONNECTED.value
            else:
                self._data_plane_outcomes[as_obj.asn] = attacker_outcome + victim_outcome