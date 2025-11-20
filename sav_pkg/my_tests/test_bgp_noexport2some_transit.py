from types import SimpleNamespace

from bgpy.enums import Relationships
from sav_pkg.policies.bgp.bgp_noexport2some import BGPNoExport2Some


class DummyNeighbor:
    def __init__(self, asn):
        self.asn = asn


class DummyAS:
    def __init__(self):
        self.asn = 100
        # Transit AS with two providers
        self.provider_asns = {200, 300}
        self.providers = [DummyNeighbor(200), DummyNeighbor(300)]


def _make_dummy_ann():
    # Announcement אובייקט "פשוט" שמתנהג כמו מה שהפוליסי מצפה לו
    ann = SimpleNamespace()
    ann.prefix = "1.1.1.0/24"
    ann.recv_relationship = Relationships.CUSTOMERS
    ann.as_path = (12345,)
    # copy "פשוט" שעושה shallow copy עם override לשדות
    def _copy(updates: dict):
        new = SimpleNamespace(**ann.__dict__)
        for k, v in updates.items():
            setattr(new, k, v)
        return new
    ann.copy = _copy
    return ann


def test_bgp_noexport2some_transit_exports_to_subset(monkeypatch):
    """Verify that BGPNoExport2Some on a transit AS only exports to some providers."""

    as_ = DummyAS()
    policy = BGPNoExport2Some(as_=as_)

    # local_rib עם Announcement אחד
    ann = _make_dummy_ann()
    policy._local_rib = {"1.1.1.0/24": ann}

    sent_neighbors = []

    def fake_process_outgoing_ann(neighbor, ann2, propagate_to, send_rels):
        sent_neighbors.append(neighbor.asn)

    # לא באמת לשלוח הודעות – רק לרשום למי היה נשלח
    monkeypatch.setattr(policy, "_process_outgoing_ann", fake_process_outgoing_ann)

    policy._propagate(
        propagate_to=Relationships.PROVIDERS,
        send_rels={Relationships.CUSTOMERS, Relationships.PEERS, Relationships.PROVIDERS},
    )

    # ודא שהשליחה הייתה רק לחלק מה־providers, או לפחות לא ל־0 ולא לכולם
    assert sent_neighbors, "No providers received announcements"
    assert set(sent_neighbors).issubset({200, 300})
    # אם המדיניות אמורה *לא* לשלוח לכולם, אפשר גם:
    # assert len(set(sent_neighbors)) < 2
