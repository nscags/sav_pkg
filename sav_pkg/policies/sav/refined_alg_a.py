from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy

from bgpy.simulation_engine import ASPA

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine
    from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario

class RefinedAlgA(BaseSAVPolicy):
    name: str = "Refined Alg A"

    @staticmethod
    def validate(
        as_obj: "AS", 
        source_prefix: str, 
        prev_hop: "AS", 
        engine: "SimulationEngine", 
        scenario: "SAVScenario",
    ):
        """
        Validates incoming packets based on Refined Alg A defined in BAR SAV draft.

        Internet draft procedure description:
        https://datatracker.ietf.org/doc/draft-ietf-sidrops-bar-sav/
        """
        i = 0
        z_i = [{prev_hop.asn}]

        while True:
            i += 1

            # Comments are direct quotes from BAR SAV draft
            # "Create AS-set A(i) of all ASNs whose ASPA data declares at least
            # one ASN in AS-set Z(i-1) as a Provider."
            a_i = set()
            for asn in z_i[i - 1]:
                tmp_as_obj = engine.as_graph.as_dict[asn]
                for customer_asn in tmp_as_obj.customer_asns:
                    if isinstance(engine.as_graph.as_dict[customer_asn].policy, ASPA):
                        a_i.add(customer_asn)

            # "Create AS-set B(i) of all customer ASNs each of which is a
            # customer of at least one ASN in AS-set Z(i-1) according to
            # unique AS_PATHs in Adj-RIBs-In of all interfaces at the BGP
            # speaker computing the SAV filter."
            b_i = set()
            for prefix_dict in as_obj.policy._ribs_in.data.values():
                for ann_info in prefix_dict.values():
                    if as_obj.policy._valid_ann(
                        ann_info.unprocessed_ann, ann_info.recv_relationship
                    ):
                        ann = ann_info.unprocessed_ann
                        as_path = ann.as_path
                        for j in range(len(as_path) - 1):
                            if as_path[j] in z_i[i - 1] and as_path[j + 1] in engine.as_graph.as_dict[as_path[j]].customer_asns:
                                b_i.add(as_path[j + 1])

            # "Form the union of AS-sets A(i) and B(i) and call it AS-set C.
            # From AS-set C, remove any ASNs that are present in Z(j), for j=1
            # to j=(i-1).  Call the resulting set Z(i)."
            c_i = a_i.union(b_i)

            for j in range(0, i):
                c_i -= z_i[j - 1]

            z_i.append(c_i)

            # "If AS-set Z(i) is null, then set i_max = i - 1 and go to Step 9.
            # Else, go to Step 4."
            if not z_i[i - 1]:
                i_max = i - 1
                break

        d = set().union(*z_i[:i_max])

        # "Select all ROAs in which the authorized origin ASN is in AS-set
        # D. Form the union of the sets of prefixes listed in the
        # selected ROAs. Name this union set of prefixes as Prefix-set P1."
        p1 = set()
        for roa in scenario.roa_infos:
            if roa.origin in d:
                p1.add(roa.prefix)

        # "Using the routes in Adj-RIBs-In of all interfaces, create a list
        # of all prefixes originated by any ASN in AS-set D.  Name this
        # set of prefixes as Prefix-set P2."
        p2 = set()
        for prefix_dict in as_obj.policy._ribs_in.data.values():
            for ann_info in prefix_dict.values():
                if as_obj.policy._valid_ann(
                    ann_info.unprocessed_ann, ann_info.recv_relationship
                ):
                    ann = ann_info.unprocessed_ann
                    if ann.origin in d:
                        p2.add(ann.prefix)

        prefixes = p1.union(p2)

        return source_prefix in prefixes