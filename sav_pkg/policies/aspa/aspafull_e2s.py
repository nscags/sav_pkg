from typing import TYPE_CHECKING
from dataclasses import replace

from bgpy.simulation_engine import ASPAFull
from bgpy.enums import Relationships

from sav_pkg.policies.bgp import BGPFullExport2Some

if TYPE_CHECKING:
    from bgpy.simulation_engine import Announcement as Ann
    

class ASPAFullExport2Some(ASPAFull, BGPFullExport2Some):
    name: str = "ASPAFull E2S"

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:  # type: ignore
        """Returns False if from peer/customer when aspa is set"""

        if len(set(ann.as_path)) != len(ann.as_path):
            seen = set()
            path_no_prepending = tuple([x for x in ann.as_path if not (x in seen or seen.add(x))])
            unprocessed_ann_no_prepending = replace(ann, as_path=path_no_prepending)
            return super()._valid_ann(unprocessed_ann_no_prepending, from_rel)

        return super()._valid_ann(ann, from_rel)