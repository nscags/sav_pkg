from .base_sav_policy import BaseSAVPolicy

from sav_pkg.enums import ASNs, Relationships, Prefixes

class BAR_SAV(BaseSAVPolicy):
    name: str = "BAR SAV"

    @staticmethod
    def validate(as_obj, prev_hop, engine, as_path):  
        
        # BAR SAV is applied to only customer and lateral peer interfaces
        if (prev_hop.asn in as_obj.provider_asns):
            return True
        else:
            # RFC specifications
            i = 0
            z = [{prev_hop.asn}]
            
            while True:
                i += 1

                # "Create AS-set A(i) of all ASNs whose ASPA data declares at least
                # one ASN in AS-set Z(i-1) as a Provider."

                # For now we assume that if an AS is adopting ASPA
                # then the adopting AS has published a list of providers
                # this isn't necessary the case
                # ASPA data somewhere?
                a_i = set()
                for asn in z[i - 1]:
                    tmp_as_obj = engine.as_graph.as_dict[asn]
                    for customer_asn in tmp_as_obj.customer_asns:
                        customer_as_obj = engine.as_graph.as_dict[customer_asn]
                        if customer_as_obj.policy.__class__.name in ['ASPA', 'ASPAFull']:
                            a_i.add(customer_asn)

                # "Create AS-set B(i) of all customer ASNs each of which is a 
                # customer of at least one ASN in AS-set Z(i-1) according to
                # unique AS_PATHs in Adj-RIBs-In of all interfaces at the BGP
                # speaker computing the SAV filter."
                b_i = set()
                for neighbor, prefix_dict in as_obj.policy._ribs_in.data.items():
                    for prefix, ann_info in prefix_dict.items():
                        ann = ann_info.unprocessed_ann
                        for j, asn in enumerate(ann.as_path):
                            if asn in z[i - 1] and asn != ann.as_path[-1]:
                                tmp_as_obj = engine.as_graph.as_dict[asn]
                                for customer_asn in tmp_as_obj.customer_asns:
                                    if customer_asn == ann.as_path[j+1]:
                                        b_i.add(customer_asn)

                c_i = a_i.union(b_i)

                for j in range(1, i):
                    c_i -= z[j - 1]

                z.append(c_i)

                if not z[i-1]:
                    i_max = i - 1
                    break

            d = set().union(*z[:i_max])


            # "Select all ROAs in which the authorized origin ASN is in AS-set
            # D. Form the union of the sets of prefixes listed in the
            # selected ROAs. Name this union set of prefixes as Prefix-set P1."
            p1 = set()
            for asn in d:
                tmp_as_obj = engine.as_graph.as_dict[asn]
                # assume any AS that adopts ROV (or ASPA) has
                # published ROA for their announced prefix 
                # (Attacker does not publish a ROA)

                # this is a wrong assumption
                # AS can adopt ROV without publishing a ROA themselves
                # For now I will leave as is but will need to change
                # Can access ROA data somewhere?

                if tmp_as_obj.policy.__class__.name in ['ROV', 'ROVFull', 'ASPA', 'ASPAFull'] and asn != ASNs.ATTACKER.value:
                    for ann in as_obj.policy._local_rib.data.values():
                        if len(ann.as_path) == 1:
                            p1.add(ann.prefix)

            # "Using the routes in Adj-RIBs-In of all interfaces, create a list
            # of all prefixes originated by any ASN in AS-set D.  Name this
            # set of prefixes as Prefix-set P2."
            p2 = set()
            for neighbor, prefix_dict in as_obj.policy._ribs_in.data.items():
                for prefix, ann_info in prefix_dict.items():
                    ann = ann_info.unprocessed_ann
                    if ann.as_path[-1] in d:
                        p2.add(prefix)

            prefixes = p1.union(p2)

            origin_as_obj = as_path[-1]

            return (origin_as_obj.asn in d) and (Prefixes.VICTIM.value in prefixes)