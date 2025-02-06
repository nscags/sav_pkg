from bgpy.simulation_engine import BGPFull

from .bgp_export2some_w_replacement import BGPExport2Some_wReplacement 

class BGPFullExport2Some_wReplacement(BGPFull, BGPExport2Some_wReplacement):
    name: str = "BGPFull E2S wR"