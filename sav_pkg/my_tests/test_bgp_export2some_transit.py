import random
from types import SimpleNamespace

from sav_pkg.policies.bgp.bgp_export2some import BGPExport2Some
from bgpy.enums import Relationships


class DummyNeighbor:
    """Minimal stand-in for a real neighbor AS object."""
    def __init__(self, asn: int):
        self.asn = asn


class DummyAS:
    """Transit AS with multiple providers."""
    def __init__(self):
        self.asn = 65000
        self.provider_asns = {1, 2, 3}
        self.providers = [DummyNeighbor(i) for i in self.provider_asns]


class FakeAnn:
    """
    Minimal Announcement replacement:
    מספיק בשביל _propagate לעבוד בלי למשוך את כל מנוע הסימולציה.
    """
    def __init__(self, prefix, recv_relationship, as_path, next_hop_asn):
        self.prefix = prefix
        self.recv_relationship = recv_relationship
        self.as_path = as_path
        self.next_hop_asn = next_hop_asn

    def copy(self, updates: dict):
        data = {
            "prefix": self.prefix,
            "recv_relationship": self.recv_relationship,
            "as_path": self.as_path,
            "next_hop_asn": self.next_hop_asn,
        }
        data.update(updates)
        return FakeAnn(**data)


def test_bgp_export2some_transit_partial_export_and_no_leak_to_zero_weight():
    """
    Transit AS with BGPExport2Some:
    * מוודא ש־_provider_export_control בוחר תת-קבוצה מה-providers
      לפי משקלים שהגדרנו.
    * מוודא ש-_propagate מייצא את ההודעה רק ל-providers עם weight > 0
      ולא ל־providers עם weight == 0.
    """

    random.seed(123)

    # Transit AS
    dummy_as = DummyAS()

    # Policy instance
    policy = BGPExport2Some(as_=dummy_as)

    original_weight_dict = policy.e2s_asn_provider_weight_dict
    original_superprefix_dict = policy.e2s_asn_provider_superprefix_dict
    original_prepending_dict = policy.e2s_asn_provider_prepending_dict

    try:
     
        policy.e2s_asn_provider_weight_dict = {
            dummy_as.asn: {
                1: 1.0,  
                2: 0.0, 
                3: 0.0, 
            }
        }

        policy.e2s_asn_provider_superprefix_dict = {}
        policy.e2s_asn_provider_prepending_dict = {}

        ann = FakeAnn(
            prefix="1.1.1.0/24",
            recv_relationship=Relationships.ORIGIN,
            as_path=(dummy_as.asn,),
            next_hop_asn=dummy_as.asn,
        )
        policy._local_rib = {"1.1.1.0/24": ann}

        sent_original = set()
        sent_other = set()

        def fake_process_outgoing_ann(neighbor, outgoing_ann, *_args):
            if outgoing_ann.prefix == "1.1.1.0/24":
                sent_original.add(neighbor.asn)
            else:
                sent_other.add(neighbor.asn)

        policy._process_outgoing_ann = fake_process_outgoing_ann

        policy._propagate(
            propagate_to=Relationships.PROVIDERS,
            send_rels={Relationships.ORIGIN},
        )

        assert sent_original, "Export2Some אמור לשלוח לפחות לספק אחד."

        assert sent_original == {1}, (
            f"ציפינו שההודעה תגיע רק ל-provider 1, "
            f"אבל בפועל נשלח ל: {sent_original}"
        )

        assert not sent_other, (
            f"לא אמורות להישלח הודעות אחרות ל-providers עם weight 0, "
            f"אבל נשלח ל: {sent_other}"
        )

    finally:
        policy.e2s_asn_provider_weight_dict = original_weight_dict
        policy.e2s_asn_provider_superprefix_dict = original_superprefix_dict
        policy.e2s_asn_provider_prepending_dict = original_prepending_dict
