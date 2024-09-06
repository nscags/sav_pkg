from .base_sav_policy import BaseSAVPolicy

class BAR_SAV(BaseSAVPolicy):
    name: str = "BAR SAV"

    def validate(self, as_obj, prev_hop, source, engine):  
        
        # BAR SAV is applied to only customer and lateral peer interfaces
        if (prev_hop.asn in as_obj.provider_asns):
            return True
        else:
            pass
        

        # prev_hop = as_k
        # get customer cone for as_k
        # augment with ASPA data

        # using roa data get prefixes those ASes are authorized to announce
        # 
        # I assume we might want to vary the percent adoption of ASPA and ROA when measuring BAR SAV
        # Use ASPA data to determine ASes within the previous hop AS (interface you are receiving the packet from) customer cone
        # ROA data is used to determine valid prefixes which can be announced by ASes discovered using ASPA data
