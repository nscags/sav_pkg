from bgpy.simulation_engine import BGPFull

from .bgp_e2s_path_prepending import BGPExport2SomePathPrepending 


class BGPFullExport2SomePathPrepending(BGPFull, BGPExport2SomePathPrepending):
    name: str = "BGPFull E2S Path Prepending"