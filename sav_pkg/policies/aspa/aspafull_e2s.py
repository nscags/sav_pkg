from bgpy.simulation_engine import ASPA

from sav_pkg.policies.bgp import BGPFullExport2Some

class ASPAFullExport2Some(ASPA, BGPFullExport2Some):
    name: str = "ASPAFull E2S"