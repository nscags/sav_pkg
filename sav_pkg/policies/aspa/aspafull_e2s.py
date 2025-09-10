from bgpy.simulation_engine import ASPAFull

from sav_pkg.policies.bgp import BGPFullExport2Some

class ASPAFullExport2Some(ASPAFull, BGPFullExport2Some):
    name: str = "ASPAFull E2S"