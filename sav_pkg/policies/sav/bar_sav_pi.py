from typing import TYPE_CHECKING
import ipaddress
from dataclasses import replace

from bgpy.simulation_engine.policies import ASPA, ROV

from .base_sav_policy import BaseSAVPolicy
from .bar_sav import BAR_SAV

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine

    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario


class BAR_SAV_PI(BaseSAVPolicy):
    name: str = "BAR-SAV PI"

    @staticmethod
    def _validate(
        as_obj: "AS",
        source_prefix: str,
        prev_hop: "AS",
        engine: "SimulationEngine",
        scenario: "SAVScenario",
    ):   
#   1.  Per procedure in Section 4, compute AS-set D and Pfx-set Q for
#       each customer interface of the AS in consideration.
        dq_set = []
        for customer_asn in as_obj.customer_asns:
            customer_as_obj = engine.as_graph.as_dict[customer_asn]
            d, q = BAR_SAV._get_as_prefix_set(
                as_obj=as_obj,
                source_prefix=source_prefix,
                prev_hop=customer_as_obj,
                engine=engine,
                scenario=scenario,
            )
            dq_set.append((d, q))

#   2.  Form the union of the AS-sets found above and call it AS-set Du.
#       Also form the union of the Pfx-sets found above and call it Pfx-
#       set Qu.
        du = set().union(*(d for d, _ in dq_set))
        qu = set().union(*(q for _, q in dq_set))

#   3.  Modify Pfx-set Qu to keep only the prefixes whose routes in the
#       RIBs-In (of the customer interfaces in consideration) are all
#       RPKI-ROV Valid and have Valid AS path per ASPA verification.
        invalid_prefixes = set()
        for prefix in qu:
            anns = []
            for customer_asn in as_obj.customer_asns:
                rib_in = as_obj.policy._ribs_in.data.get(customer_asn, {})
                for ann_info in rib_in.values():
                    if as_obj.policy._valid_ann(
                        ann_info.unprocessed_ann, ann_info.recv_relationship
                    ) and ann_info.unprocessed_ann.prefix == prefix:
                        anns.append(ann_info)

            if anns:
                aspa = ASPA(as_=as_obj)
                rov = ROV(as_=as_obj)

                for ann in anns:
                    if len(set(ann.unprocessed_ann.as_path)) != len(ann.unprocessed_ann.as_path):  # path prepending
                        path_no_prepending = ann.unprocessed_ann.as_path[:-2]
                    else:
                        path_no_prepending = ann.unprocessed_ann.as_path

                    unprocessed_ann_no_prepending = replace(ann.unprocessed_ann, as_path=path_no_prepending)

                    valid = (
                        aspa._valid_ann(unprocessed_ann_no_prepending, ann.recv_relationship) and
                        rov._valid_ann(unprocessed_ann_no_prepending, ann.recv_relationship)
                    )

                    if not valid:
                        invalid_prefixes.add(prefix)
                        break

        qu -= invalid_prefixes

#   4.  Further modify Pfx-set Qu to keep only the prefixes that have all
#       their allowed origin ASes (per ROAs) contained within AS-set Du.
        for roa in scenario.roa_infos:
            if roa.prefix in qu and roa.origin not in du:
                qu.remove(roa.prefix)

#   5.  Further modify Pfx-set Qu to keep only the prefixes with all
#       feasible routes from their respective origin ASes to the local AS
#       (i.e., AS doing SAV) such that each AS in the AS path of each
#       route has all its Provider ASes (per ASPAs) contained within AS-
#       set Du.  Call the resulting modified set as Pfx-set S.
        s = set()
        for prefix in qu:
            anns = []
            valid = True
            for prefix_dict in as_obj.policy._ribs_in.data.values():
                for ann_info in prefix_dict.values():
                    ann = ann_info.unprocessed_ann
                    if ann.prefix == prefix and as_obj.policy._valid_ann(ann, ann_info.recv_relationship):
                        anns.append(ann)

            if anns:
                for ann in anns:
                    for asn in ann.as_path:
                        as_on_path_obj = engine.as_graph.as_dict.get(asn)
                        if isinstance(as_on_path_obj.policy, ASPA):
                            if any(provider not in du for provider in as_on_path_obj.provider_asns):
                                valid = False
                                break
                        elif asn not in du:
                            valid = False
                            break
                    if not valid:
                        break
                if valid:
                    s.add(prefix)

#   6.  Subtract Pfx-set S from the set of allowed prefixes that pertain
#       to loose uRPF for the Provider interfaces.  Call this reduced set
#       as Pfx-set Ga.
        ga = set()
        for prefix, _ in as_obj.policy._local_rib.data.items():
            if prefix not in s:
                ga.add(prefix) 

#   7.  From Pfx-set Ga, subtract (a) any prefixes originated by the
#       local AS that are single-homed and (b) any internal-use-only
#       prefixes of the local AS.  Call the resulting set as Pfx-set G.
#       NOTE: We do not simulate either of these instances
        g = ga

#   8.  Apply Pfx-set G as the allow list for ingress SAV at each
#       provider interface of the local AS, after possibly extending Pfx-
#       set G using an ACL configured for that provider interface.
        src_prefix = ipaddress.ip_network(source_prefix)
        return any(src_prefix.subnet_of(ipaddress.ip_network(prefix)) for prefix in g)