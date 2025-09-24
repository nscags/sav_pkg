from bgpy.simulation_engine import ASPA

from sav_pkg.policies.bgp import BGPNoExport2Some


class ASPANoExport2Some(ASPA, BGPNoExport2Some):
    name: str = "ASPA No-E2S"