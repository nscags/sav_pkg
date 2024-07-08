from typing import Optional
from dataclasses import dataclass

from bgpy.simulation_framework import ScenarioConfig
from bgpy.enums import ASGroups

@dataclass(frozen=True)
class SAVScenarioConfig(ScenarioConfig):
    num_attackers: int = 1
    num_victims: int = 1

    num_reflectors: int = 1
    reflector_subcategory_attr: Optional[str] = ASGroups.STUBS_OR_MH.value
    override_reflector_asns: Optional[frozenset[int]] = None


    def __post_init__(self):
        super().__post_init__()