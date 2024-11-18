from .base_sav_policy import BaseSAVPolicy
from .loose_urpf import LooseuRPF

class BAR_SAV(BaseSAVPolicy):
    name: str = "BAR SAV"

    @staticmethod
    def validate(as_obj, source_prefix, prev_hop, engine, scenario):  
        """
        Validates incoming packets based on BAR SAV.
        
        Internet draft procedure description:
        https://datatracker.ietf.org/doc/draft-ietf-sidrops-bar-sav/
        """
        # Loose uRPF is applied to provider interfaces
        # BAR SAV is applied to only customer and lateral peer interfaces
        if prev_hop.asn in as_obj.provider_asns:
            LooseuRPF.validate(
                as_obj=as_obj,
                source_prefix=source_prefix,
                prev_hop=prev_hop,
                engine=engine
            )
        else:
            i = 0
            z = [{prev_hop.asn}]
            # print(f"Interface: {z}")
            
            while True:
                i += 1

                # "Create AS-set A(i) of all ASNs whose ASPA data declares at least
                # one ASN in AS-set Z(i-1) as a Provider."

                # For now we assume that if an AS is adopting ASPA
                # then the adopting AS has published a list of providers
                # this isn't necessary the case, however don't have ASPA data
                a_i = set()
                for asn in z[i - 1]:
                    tmp_as_obj = engine.as_graph.as_dict[asn]
                    for customer_asn in tmp_as_obj.customer_asns:
                        customer_as_obj = engine.as_graph.as_dict[customer_asn]
                        if customer_as_obj.policy.name in ['ASPA', 'ASPA Full']:
                            a_i.add(customer_asn)

                # print(f"A_i: {a_i}")

                # "Create AS-set B(i) of all customer ASNs each of which is a 
                # customer of at least one ASN in AS-set Z(i-1) according to
                # unique AS_PATHs in Adj-RIBs-In of all interfaces at the BGP
                # speaker computing the SAV filter."
                b_i = set()
                for prefix_dict in as_obj.policy._ribs_in.data.values():
                    for ann_info in prefix_dict.values():
                        if as_obj.policy._valid_ann(ann_info.unprocessed_ann, ann_info.recv_relationship):
                            ann = ann_info.unprocessed_ann
                            print(ann)
                            for j, asn in enumerate(ann.as_path):
                                if asn in z[i - 1] and j+1 != len(ann.as_path):
                                    b_i.add(ann.as_path[j + 1])
                # print(f"B_i: {b_i}")

                c_i = a_i.union(b_i)

                # print(f"C_{i}: {c_i}")

                for j in range(1, i):
                    c_i -= z[j - 1]

                z.append(c_i)

                # print(f"Z: {z}\n")

                if not z[i-1]:
                    i_max = i - 1
                    break

            d = set().union(*z[:i_max])
            # print(f"D: {d}")

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
                    if as_obj.policy._valid_ann(ann_info.unprocessed_ann, ann_info.recv_relationship):
                        ann = ann_info.unprocessed_ann
                        if ann.origin in d:
                            p2.add(ann.prefix)

            prefixes = p1.union(p2)

            # print(f"Prefixes {prefixes}")

            # If the victim's prefix is within the list of prefixes
            return source_prefix in prefixes