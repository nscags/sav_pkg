from dataclasses import dataclass
from typing import Optional

from bgpy.enums import ASGroups, Plane, Outcomes

from sav_pkg.policies.sav.base_sav_policy import BaseSAVPolicy


@dataclass(frozen=True, slots=True)
class MetricKey:
    """Key for storing data within each metric"""

    plane: Plane
    as_group: ASGroups
    outcome: Outcomes
    PolicyCls: Optional[type[BaseSAVPolicy]] = None