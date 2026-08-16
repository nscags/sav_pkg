from bgpy.simulation_engine import ASRAFull, BaseSimulationEngine, Policy

from .sav_scenario import SAVScenario


class SAVScenarioKnownPeers(SAVScenario):
    """
    Identical to SAVScenario but for every bilateral peer link in the graph,
    at least one adopts the ASRA.
    """

    #####################
    # Policy assignment #
    #####################

    def get_policy_cls(self, as_obj) -> type[Policy]:
        if as_obj.asn in self._asra_asns:
            return ASRAFull
        return super().get_policy_cls(as_obj)

    ###########################
    # Get ctrl-plane adopters #
    ###########################

    def _get_ctrl_plane_adopters(
        self,
        engine: BaseSimulationEngine | None,
    ) -> frozenset[int]:
        """
        Assigns ASRA to peer links, ctrl plane adopters are sampled from remaining ASes
        """
        asra_asns: set[int] = set()
        if engine is not None:
            for as_obj in engine.as_graph:
                for peer_asn in as_obj.peer_asns:
                    if as_obj.asn in asra_asns or peer_asn in asra_asns:
                        continue
                    if as_obj.asn not in self.attacker_asns:
                        asra_asns.add(as_obj.asn)
                    elif peer_asn not in self.attacker_asns:
                        asra_asns.add(peer_asn)
        self._asra_asns = frozenset(asra_asns)

        return super()._get_ctrl_plane_adopters(engine)
