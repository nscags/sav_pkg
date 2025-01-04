from bgpy.simulation_engine import BGPFull

from sav_pkg.simulation_engine.policies.bgp.bgp_export2some import BGPExport2Some 

class BGPFullExport2Some(BGPFull, BGPExport2Some):
    name: str = "BGPFull Export2Some"