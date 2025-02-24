from bgpy.simulation_engine import ASPA

from sav_pkg.simulation_engine.policies.rov import ROVExport2Some

class ASPAExport2Some(ASPA, ROVExport2Some):
    name: str = "ASPA E2S"