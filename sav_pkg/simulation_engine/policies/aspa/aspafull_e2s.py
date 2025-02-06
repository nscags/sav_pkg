from bgpy.simulation_engine import ASPAFull

from sav_pkg.simulation_engine.policies.rov import ROVFullExport2Some

class ASPAFullExport2Some(ASPAFull, ROVFullExport2Some):
    name: str = "ASPAFull E2S"