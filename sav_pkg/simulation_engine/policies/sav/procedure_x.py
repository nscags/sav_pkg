from typing import TYPE_CHECKING

from .base_sav_policy import BaseSAVPolicy

if TYPE_CHECKING:
    from bgpy.as_graphs.base import AS
    from bgpy.simulation_engine import SimulationEngine
    from sav_pkg.simulation_framework import SAVScenario

class ProcedureX(BaseSAVPolicy):
    name: str = "Procedure X"

    @staticmethod
    def validate(
        as_obj: "AS", 
        source_prefix: str, 
        prev_hop: "AS", 
        engine: "SimulationEngine", 
        scenario: "SAVScenario",
    ):
        """
        Validates incoming packets based on Procedure X defined in the
        BAR SAV draft. This policy is specifically for the case in which there is
        full adoption of both ASPA and ROV. Additionally, we assume that all ASes have published
        their corresponding RPKI data (SPAS and ROA). 

        Internet draft procedure description:
        https://datatracker.ietf.org/doc/draft-ietf-sidrops-bar-sav/
        """
        # Let the Customer or Lateral Peer ASN be denoted as AS-k.
        as_k = prev_hop.asn

        # Let i = 1.  Initialize: AS-set S(1) = {AS-k}.
        i = 0
        S = [{as_k}]

        while True:
            # Increment i to i+1.
            i += 1

            # Create AS-set S(i) of all ASNs whose ASPA data declares at least
            # one ASN in AS-set S(i-1) as a Provider.
            S_i = set()
            for asn in S[i - 1]:
                tmp_as_obj = engine.as_graph.as_dict[asn]
                if not tmp_as_obj:
                    continue  # Skip non-existent ASes

                for customer_asn in tmp_as_obj.customer_asns:
                    customer_as_obj = engine.as_graph.as_dict[customer_asn]
                    if customer_as_obj and customer_as_obj.policy.name in ["ASPA", "ASPA Full", "PseudoASPAFull"]: # first part added to prevent attributeError when trying to access .policy.name
                        S_i.add(customer_asn)

            # If AS-set S(i) is null, then set i_max = i - 1 and go to Step 6.
            # Else, go to Step 3.
            # if not S[i - 1]:
            #     i_max = i - 1
            #     break
            # else:
            #     S.append(S_i)

            # Append the newly computed AS-set S(i) to the list of sets
            S.append(S_i)
            # If S(i) is empty, stop iterating and set i_max = i
            # This means no new ASes were added, so the expansion has reached its limit
            if not S_i:
                i_max = i  # Store the final depth of expansion
                break  # Exit the loop
            


    
        

            

        # Form the union of the sets, S(i), i = 1, 2, ..., i_max, and name
        # this union as AS-set A.
        A = set().union(*S[:i_max])
        
        # Build P-set using optimized dictionary lookup
        roa_dict = {roa.origin: set() for roa in scenario.roa_infos}
        for roa in scenario.roa_infos:
            roa_dict[roa.origin].add(roa.prefix)

        P = set().union(*(roa_dict.get(asn, set()) for asn in A))

        # Validate prefix
        return source_prefix in P if P else False  # Explicit failure if P-set is empty