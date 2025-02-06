from bgpy.simulation_engine import BGPFull

from .bgp_export2some import BGPExport2Some 

class BGPFullExport2Some(BGPFull, BGPExport2Some):
    name: str = "BGPFull E2S"