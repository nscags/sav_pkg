from bgpy.simulation_engine import ROVFull

from sav_pkg.simulation_engine import BGPFullExport2Some 

class ROVFullExport2Some(ROVFull, BGPFullExport2Some):
    name: str = "ROVFull E2S"