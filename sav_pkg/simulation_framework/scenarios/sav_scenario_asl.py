from typing import TYPE_CHECKING

from roa_checker import ROA

from bgpy.shared.enums import ASGroups, SpecialPercentAdoptions
from bgpy.simulation_engine import BaseSimulationEngine

from sav_pkg.enums import ASLLocations
from sav_pkg.simulation_framework.scenarios.sav_scenario_config import SAVScenarioConfig

from .sav_scenario import SAVScenario

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine import Announcement as Ann


# An attacker's placement: its location, and the t it could go through mapped
# to the w that t could hand the packet to (empty unless CUSTOMER_OF_PEER)
Placement = tuple[ASLLocations, dict[int, frozenset[int]]]

# Reflectors with no valid attacker placement are redrawn up to this many times
MAX_REFLECTOR_DRAWS = 10


class SAVScenarioASL(SAVScenario):
    """
    Scenario for Attacker Selected Location attack model.
    Spoofing attacker but selects location to be in one of the follwing places:
    (1) in the provider cone of the validating AS v
    (2) customer of a non SAV adopting AS t such that either
        (a) t is in the provider cone of v
        (b) t is a bilateral peer of a non SAV adopting AS in the provider cone of v
    """

    def __init__(
        self,
        *,
        scenario_config: SAVScenarioConfig,
        percent_adoption: float | SpecialPercentAdoptions = 0,
        engine: BaseSimulationEngine | None = None,
        attacker_asns: frozenset[int] | None = None,
        victim_asns: frozenset[int] | None = None,
        adopting_asns: frozenset[int] | None = None,
        reflector_asns: frozenset[int] | None = None,
    ):
        assert scenario_config.ScenarioCls == self.__class__, (
            "The config's scenario class is "
            f"{scenario_config.ScenarioCls.__name__}, but the scenario used is "
            f"{self.__class__.__name__}"
        )
        assert scenario_config.num_reflectors == 1, (
            "SAVScenarioASL places the attacker relative to one validating AS, "
            f"so num_reflectors must be 1, not {scenario_config.num_reflectors}"
        )

        self.scenario_config: SAVScenarioConfig = scenario_config
        self.percent_adoption: float | SpecialPercentAdoptions = percent_adoption

        # The attacker is placed relative to the reflector, so unlike
        # SAVScenario the order is victim -> reflector -> attacker. No attacker
        # is chosen yet, and the victim/reflector candidate filters read this.
        #
        # The attacker_asns bgpy hands over from the previous scenario of the
        # trial are ignored on purpose: the reflector and attacker are both
        # re-derived from the victim here (see _get_asl_reflector_asns), which
        # already keeps them identical across the trial, and also stays
        # correct when scenario configs in the trial differ in asl_locations.
        self.attacker_asns: frozenset[int] = frozenset()
        self.victim_asns: frozenset[int] = self._get_victim_asns(
            scenario_config.override_victim_asns, victim_asns, engine
        )
        self.reflector_asns, placements = self._get_asl_reflector_asns(
            scenario_config.override_reflector_asns, reflector_asns, engine
        )
        self.attacker_asns = self._get_asl_attacker_asns(
            scenario_config.override_attacker_asns, placements
        )
        # The t (and w) each attacker goes through, which never adopt SAV
        self._asl_non_sav_adopters: frozenset[int] = self._get_asl_non_sav_adopters(
            placements
        )

        # From here on, the same as SAVScenario
        # adopting_asns = SAV adopters
        self.adopting_asns: frozenset[int] = self._get_sav_adopting_asns(
            adopting_asns, engine
        )
        self.sav_policy_asn_dict = self._build_sav_policy_asn_dict()

        # Control-plane adopters (e.g. ASPA) - separate from SAV adoption
        self._ctrl_plane_adopters: frozenset[int] = self._get_ctrl_plane_adopters(engine)

        if scenario_config.override_announcements is not None:
            self.announcements: tuple["Ann", ...] = scenario_config.override_announcements
            self.roas: tuple[ROA, ...] = scenario_config.override_roas or ()
        else:
            self.announcements = self._get_announcements(engine=engine)
            self.roas = self._get_roas(announcements=self.announcements, engine=engine)

        self._reset_and_add_roas_to_roa_checker()

        self.ordered_prefix_subprefix_dict: dict[str, list[str]] = (
            self._get_ordered_prefix_subprefix_dict()
        )

    ########################
    # Reflector / attacker #
    ########################

    def _get_asl_reflector_asns(
        self,
        override_reflector_asns: frozenset[int] | None,
        reflector_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
    ) -> tuple[frozenset[int], dict[int, Placement]]:
        """
        Returns the reflector (v) and every AS that could attack it from an
        enabled location

        A reflector no attacker can be placed against (e.g. a tier 1, whose
        provider cone is empty) is redrawn under a new salt. No attacker is
        chosen yet, so _sample_seed depends on the victim alone, and every
        scenario of the trial redraws the same sequence and lands on the same
        reflector.
        """
        assert engine, "SAVScenarioASL needs the engine to place the attacker"

        fixed = (
            override_reflector_asns
            if override_reflector_asns is not None
            else reflector_asns
        )
        if fixed is not None:
            return frozenset(fixed), self._get_asl_placements(engine, fixed)

        possible = self._get_possible_reflector_asns(engine, self.percent_adoption)
        for draw in range(MAX_REFLECTOR_DRAWS):
            salt = "reflector" if draw == 0 else f"reflector#{draw}"
            candidate = frozenset(self._sample_asns(possible, 1, salt))
            placements = self._get_asl_placements(engine, candidate)
            if len(placements) >= self.scenario_config.num_attackers:
                return candidate, placements

        raise ValueError(
            f"No reflector with an attacker placement in "
            f"{sorted(x.value for x in self.scenario_config.asl_locations)} "
            f"after {MAX_REFLECTOR_DRAWS} draws"
        )

    def _get_asl_attacker_asns(
        self,
        override_attacker_asns: frozenset[int] | None,
        placements: dict[int, Placement],
    ) -> frozenset[int]:
        """
        Draws the attacker uniformly from every AS with an enabled placement

        Seeded by the victim alone for the same reason as the reflector, with
        asl_locations in the salt so each set of locations gets its own draw.
        """
        if override_attacker_asns is not None:
            unplaced = override_attacker_asns - placements.keys()
            if unplaced:
                raise ValueError(
                    f"Attacker(s) {sorted(unplaced)} have no placement in "
                    f"{sorted(x.value for x in self.scenario_config.asl_locations)} "
                    f"relative to reflector(s) {sorted(self.reflector_asns)}"
                )
            return frozenset(override_attacker_asns)

        locations = ",".join(
            sorted(x.value for x in self.scenario_config.asl_locations)
        )
        return frozenset(
            self._sample_asns(
                frozenset(placements),
                self.scenario_config.num_attackers,
                f"attacker:{locations}",
            )
        )

    def _get_asl_non_sav_adopters(
        self,
        placements: dict[int, Placement],
    ) -> frozenset[int]:
        """
        Picks the t (and w) each attacker goes through

        Only one t (and one w) is needed for the attacker to hold its position,
        so only those are kept from adopting SAV. The attacker still sends
        along its own best route, which is not forced to go through them.
        """
        non_adopters: set[int] = set()
        for attacker_asn in sorted(self.attacker_asns):
            location, t_ws = placements[attacker_asn]
            if location == ASLLocations.PROVIDER_CONE:
                continue
            (t,) = self._sample_asns(frozenset(t_ws), 1, f"asl_t:{attacker_asn}")
            non_adopters.add(t)
            if location == ASLLocations.CUSTOMER_OF_PEER:
                (w,) = self._sample_asns(t_ws[t], 1, f"asl_w:{attacker_asn}")
                non_adopters.add(w)
        return frozenset(non_adopters)

    def _get_asl_placements(
        self,
        engine: BaseSimulationEngine,
        reflector_asns: frozenset[int],
    ) -> dict[int, Placement]:
        """
        Maps every AS that could attack v from an enabled location to its
        placement

        Each AS takes the first location it qualifies for, so the three never
        overlap, and restricting asl_locations to one location evaluates only
        attackers that actually depend on it:
        (1) PROVIDER_CONE: in v's provider cone
        (2a) CUSTOMER_OF_PROVIDER_CONE: a direct customer of a t in v's
             provider cone
        (2b) CUSTOMER_OF_PEER: a direct customer of a t outside v's provider
             cone that peers with a w inside it

        (2) takes direct customers only. Any deeper and the packet enters a
        second AS on its customer interface, where it could be filtered.
        t and w are kept from adopting SAV, so neither can be v itself or an
        AS hardcoded to adopt SAV.
        """
        (v,) = reflector_asns
        cone = self._get_provider_cone(engine.as_graph.as_dict[v])
        hardcoded_sav = self.scenario_config.hardcoded_asn_sav_dict.keys()
        # ASes in v's provider cone that can be kept from adopting SAV
        forceable_cone = cone.difference(hardcoded_sav)
        enabled = self.scenario_config.asl_locations

        candidates = engine.as_graph.asn_groups[ASGroups.ALL_WOUT_IXPS.value]
        candidates = candidates.difference(reflector_asns, self.victim_asns)

        # Many ASes share providers, so remember each t's peers in the cone
        peers_in_cone: dict[int, frozenset[int]] = dict()

        placements: dict[int, Placement] = dict()
        for asn in candidates:
            as_obj = engine.as_graph.as_dict[asn]

            # (1)
            if asn in cone:
                placement: Placement = (ASLLocations.PROVIDER_CONE, dict())
            # (2a)
            elif ts := as_obj.provider_asns & forceable_cone:
                placement = (
                    ASLLocations.CUSTOMER_OF_PROVIDER_CONE,
                    {t: frozenset() for t in ts},
                )
            # (2b)
            else:
                t_ws: dict[int, frozenset[int]] = dict()
                for t_obj in as_obj.providers:
                    t = t_obj.asn
                    if t == v or t in cone or t in hardcoded_sav:
                        continue
                    ws = peers_in_cone.get(t)
                    if ws is None:
                        ws = t_obj.peer_asns & forceable_cone
                        peers_in_cone[t] = ws
                    if ws:
                        t_ws[t] = ws
                if not t_ws:
                    continue
                placement = (ASLLocations.CUSTOMER_OF_PEER, t_ws)

            if placement[0] in enabled:
                placements[asn] = placement
        return placements

    @staticmethod
    def _get_provider_cone(as_obj: "AS") -> frozenset[int]:
        """Every AS reachable by following providers up from as_obj"""

        cone: set[int] = set()
        stack = list(as_obj.providers)
        while stack:
            current = stack.pop()
            if current.asn not in cone:
                cone.add(current.asn)
                stack.extend(current.providers)
        return frozenset(cone)

    ################
    # SAV adopters #
    ################

    def _get_sav_adopting_asns(
        self,
        adopting_asns: frozenset[int] | None,
        engine: BaseSimulationEngine | None,
    ) -> frozenset[int]:
        """
        Same as SAVScenario, minus t and w

        _preset_sav_asns already keeps t and w out of the random draw. This
        also strips them from adopters that are handed in: override_sav_asns,
        or bgpy passing along another scenario config's adopters in the trial.
        """
        adopters = super()._get_sav_adopting_asns(adopting_asns, engine)
        return adopters.difference(self._asl_non_sav_adopters)

    @property
    def _preset_sav_asns(self) -> frozenset[int]:
        """t and w are left out of the SAV adopter pool, even at 100%"""

        return super()._preset_sav_asns | self._asl_non_sav_adopters
