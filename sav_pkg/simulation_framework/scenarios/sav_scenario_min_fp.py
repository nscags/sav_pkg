from bgpy.simulation_engine import ASPAFull, ASRAFull, BaseSimulationEngine, Policy

from .sav_scenario_known_peers import SAVScenarioKnownPeers


class SAVScenarioMinFP(SAVScenarioKnownPeers):
    """
    Minimum assumptions/conditions needed for BSPI++ to have no false positives.
    Current assumptions: known peers (at least one ASRA adopting AS in each bilateral peer relationship)
                         provider cone of the source (victim) adopts ASPA (except for the already defined ASRA ASes)
    """

    _aspa_asns: frozenset[int] = frozenset()

    def get_policy_cls(self, as_obj) -> type[Policy]:
        if as_obj.asn in self._asra_asns:
            return ASRAFull
        if as_obj.asn in self._aspa_asns:
            return ASPAFull
        return super().get_policy_cls(as_obj)

    def _get_ctrl_plane_adopters(
        self,
        engine: BaseSimulationEngine | None,
    ) -> frozenset[int]:
        """
        """
        aspa_asns: set[int] = set()
        if engine is not None:
            aspa_asns = self._get_victim_provider_cone(engine)
            aspa_asns -= self.attacker_asns
        self._aspa_asns = frozenset(aspa_asns)

        return super()._get_ctrl_plane_adopters(engine)

    def _get_victim_provider_cone(
        self,
        engine: BaseSimulationEngine,
    ) -> set[int]:
        """
        """
        as_dict = engine.as_graph.as_dict

        cone: set[int] = set()
        stack = [as_dict[asn] for asn in self.victim_asns]
        while stack:
            as_obj = stack.pop()
            if as_obj.asn in cone:
                continue
            cone.add(as_obj.asn)
            stack.extend(as_obj.providers)

        return cone

    @property
    def _preset_asns(self) -> frozenset[int]:
        return super()._preset_asns | self._aspa_asns
