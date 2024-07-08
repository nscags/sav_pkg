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
        self._reflector_ann_dict: dict[AS, Optional["Ann"]] = {
            # Get the most specific ann in the rib
            as_obj: self._get_reflector_ann(as_obj)
            for as_obj in engine.as_graph
        }
        self._data_plane_outcomes: dict[int, int] = dict()
        self._control_plane_outcomes: dict[int, int] = dict()
        self.outcomes = {
            Plane.DATA.value: self._data_plane_outcomes,
            Plane.CTRL.value: self._control_plane_outcomes,
        }
        self.data_plane_tracking: bool = data_plane_tracking

    def _get_reflector_ann(self, as_obj: AS) -> Optional["Ann"]:
        """
        Get all reflector announcements for each AS in graph
        """
        for ann in as_obj.policy._local_rib.data.values():
            if ann.as_path[-1] in self.scenario.reflector_asns:
                return ann
        return None

    def analyze(self) -> dict[int, dict[int, tuple[int]]]:
        """
        data plane analysis -> outcomes
        """

        for as_obj in self.engine.as_graph:
            if (as_obj.asn in self.scenario.attacker_asns or 
                as_obj.asn in self.scenario.victim_asns):
                if self.data_plane_tracking:
                    # Gets AS outcome and stores it in the outcomes dict
                    self._get_as_outcome_data_plane(as_obj)
                self._get_other_as_outcome_hook(as_obj)

        for as_obj in self.engine.as_graph:
            if self._data_plane_outcomes.get(as_obj.asn) is None:
                self._data_plane_outcomes[as_obj.asn] = Outcomes.NOT_ON_PATH.value
    
        return self.outcomes

    ####################
    # Data plane funcs #
    ####################

    # TODO: Traceback from attacker to reflector
    #       and from victim (legit_sender) to reflector
    #       at each AS check if it performs SAV
    #       if so, run SAV and see if packet would be filtered
    #       similar to what is done now for "data plane" tracking

    def _get_as_outcome_data_plane(self, as_obj: AS) -> int:
        """
        Traceback from attacker->reflector and vitcim->reflector
        """

        if as_obj.asn in self.scenario.attacker_asns:
            spoofed_packet = True
        elif as_obj.asn in self.scenario.victim_asns:
            spoofed_packet = False

        while True:
            reflector_ann = self._reflector_ann_dict[as_obj]
            outcome_int = self._determine_as_outcome_data_plane(as_obj, reflector_ann, spoofed_packet)

            self._data_plane_outcomes[as_obj.asn] = outcome_int
            
            if as_obj.asn in self.scenario.reflector_asns:
                break
            else:
                as_obj = self.engine.as_graph.as_dict[reflector_ann.next_hop_asn]

    def _determine_as_outcome_data_plane(
        self, as_obj: AS, reflector_ann: Optional["Ann"], spoofed_packet
    ) -> int:
        """
        check if AS is deploying SAV
        run SAV policy
        determine outcome
        """

        # Check if as_obj is deploying SAV
        # if yes:
        #   run SAV policy and determine outcome
        # if no:
        #   forward packet to next AS

        # Attacker and Victim ASes (likely not deploying SAV)
        if as_obj.asn in self.scenario.attacker_asns:
            return Outcomes.ON_ATTACKER_PATH.value
        elif as_obj.asn in self.scenario.victim_asns:
            return Outcomes.ON_ATTACKER_PATH.value
        
        # Determine reflector outcome (likely always deploying SAV)
        elif as_obj.asn in self.scenario.reflector_asns:
            # *** deploy SAV policy ***
            if spoofed_packet:
                return Outcomes.FALSE_NEGATIVE.value
            elif not spoofed_packet:
                return Outcomes.TRUE_POSITIVE.value
            
        # ASes along path
        else:
            if spoofed_packet:
                return Outcomes.ON_ATTACKER_PATH.value
            elif not spoofed_packet:
                return Outcomes.ON_VICTIM_PATH.value