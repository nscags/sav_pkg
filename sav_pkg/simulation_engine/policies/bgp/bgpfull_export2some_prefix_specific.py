from bgpy.simulation_engine import BGPFull

from .bgp_export2some_prefix_specific import BGPExport2SomePrefixSpecific 

class BGPFullExport2SomePrefixSpecific(BGPFull, BGPExport2SomePrefixSpecific):
    name: str = "BGPFull E2S PS"