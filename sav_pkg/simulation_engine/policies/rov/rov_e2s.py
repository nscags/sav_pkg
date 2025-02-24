from bgpy.simulation_engine import ROV

from sav_pkg.simulation_engine import BGPExport2Some 

class ROVExport2Some(ROV, BGPExport2Some):
    name: str = "ROV E2S"