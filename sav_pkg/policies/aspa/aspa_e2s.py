from bgpy.simulation_engine import ASPA

from sav_pkg.policies.bgp import BGPExport2Some

class ASPAExport2Some(ASPA, BGPExport2Some):
    name: str = "ASPA E2S"