from bgpy.simulation_engine import BGPFull

from .bgp_noexport2some import BGPNoExport2Some 


class BGPFullNoExport2Some(BGPFull, BGPNoExport2Some):
    name: str = "BGPFull No-E2S"