from bgpy.simulation_engine import BGPFull

from .bgp_e2s_supersub import BGPExport2SomeSuperSubPrefix 


class BGPFullExport2SomeSuperSubPrefix(BGPFull, BGPExport2SomeSuperSubPrefix):
    name: str = "BGPFull E2S Super/Sub Prefix"