from typing import Any, Optional, TYPE_CHECKING

from frozendict import frozendict

from bgpy.enums import Relationships
from bgpy.simulation_engine import Policy
from bgpy.simulation_engine import SimulationEngine

from sav_pkg.simulation_engine import BaseSAVPolicy

# https://stackoverflow.com/a/57005931/8903959
if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    from bgpy.simulation_framework import Scenario


class SAVSimulationEngine(SimulationEngine):
    """Python simulation engine representation"""

    ###############
    # Setup funcs #
    ###############

    def setup(
        self,
        announcements: tuple["Ann", ...] = (),
        BasePolicyCls: type[Policy] = Policy,
        non_default_asn_cls_dict: frozendict[int, type[Policy]] = (
            frozendict()  # type: ignore
        ),
        prev_scenario: Optional["Scenario"] = None,
        attacker_asns: frozenset[int] = frozenset(),
        AttackerBasePolicyCls: Optional[type[Policy]] = None,
        reflector_asns: frozenset[int] = frozenset(),
        BaseSAVPolicyCls: Optional[type[BaseSAVPolicy]] = None
    ) -> frozenset[type[Policy]]:
        """Sets AS classes and seeds announcements"""

        policies_used: frozenset[type[Policy]] = self._set_as_classes(
            BasePolicyCls,
            non_default_asn_cls_dict,
            prev_scenario,
            attacker_asns,
            AttackerBasePolicyCls,
            reflector_asns,
            BaseSAVPolicyCls
        )
        self._seed_announcements(announcements, prev_scenario)
        self.ready_to_run_round = 0
        return policies_used

    def _set_as_classes(
        self,
        BasePolicyCls: type[Policy],
        non_default_asn_cls_dict: frozendict[int, type[Policy]],
        prev_scenario: Optional["Scenario"] = None,
        attacker_asns: frozenset[int] = frozenset(),
        AttackerBasePolicyCls: Optional[type[Policy]] = None,
        reflector_asns: frozenset[int] = frozenset(),
        BaseSAVPolicyCls: Optional[type[BaseSAVPolicy]] = None
    ) -> frozenset[type[Policy]]:
        """Resets Engine ASes and changes their AS class

        We do this here because we already seed from the scenario
        to allow for easy overriding. If scenario controls seeding,
        it doesn't make sense for engine to control resetting either
        and have each do half and half
        """

        policy_classes_used = set()
        # Done here to save as much time  as possible
        for as_obj in self.as_graph:
            # Delete the old policy and remove references so that RAM can be reclaimed
            del as_obj.policy.as_
            # set the AS class to be the proper type of AS
            Cls = non_default_asn_cls_dict.get(as_obj.asn, BasePolicyCls)
            if AttackerBasePolicyCls and as_obj.asn in attacker_asns:
                Cls = AttackerBasePolicyCls
            as_obj.policy = Cls(as_=as_obj)
            policy_classes_used.add(Cls)

            if BaseSAVPolicyCls and as_obj.asn in reflector_asns:
                as_obj.policy.source_address_validation_policy = BaseSAVPolicyCls

        # NOTE: even though the code below is more efficient than the code
        # above, for some reason it just breaks without erroring
        # likely a bug in pypy's weak references
        # for some reason the attacker is just never seeded the announcements
        # AttackerBasePolicyCls takes precendence for attacker_asns
        # if AttackerBasePolicyCls is not None:
        #    policy_classes_used.add(AttackerBasePolicyCls)
        #    for asn in attacker_asns:
        #        # Delete the old policy and remove references for RAM
        #        del as_obj.policy.as_
        #        # set the AS class to be the proper type of AS
        #        as_obj.policy = AttackerBasePolicyCls(as_=as_obj)

        return frozenset(policy_classes_used)