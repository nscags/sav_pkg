from dataclasses import dataclass

# from typing import Optional
from bgpy.enums import ASGroups, Plane

from sav_pkg.enums import Outcomes


@dataclass(frozen=True, slots=True)
class MetricKey:
    """Key for storing data within each metric"""

    plane: Plane
    as_group: ASGroups
    outcome: Outcomes
    PolicyCls = None
