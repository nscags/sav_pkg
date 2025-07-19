from bgpy.simulation_engine import ASPAFull

from sav_pkg.policies.bgp import BGPFullNoExport2Some

class ASPAFullNoExport2Some(ASPAFull, BGPFullNoExport2Some):
    name: str = "ASPAFull No-E2S"