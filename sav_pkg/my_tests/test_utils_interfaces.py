from sav_pkg.utils.utils import get_applied_interfaces, DEFAULT_SAV_POLICY_INTERFACE_DICT
from sav_pkg.enums import Interfaces
from types import SimpleNamespace


class DummyAS:
    def __init__(self):
        self.customer_asns = {1, 2}
        self.peer_asns = {3}
        self.provider_asns = {4, 5}


class DummyScenarioConfig:
    def __init__(self, override=None):
        self.override_default_interface_dict = override or {}


class DummyPolicy:
    def __init__(self, name: str):
        self.name = name


def test_get_applied_interfaces_default():
    as_obj = DummyAS()
    scenario = SimpleNamespace(
        scenario_config=DummyScenarioConfig()
    )
    sav_policy = DummyPolicy("Strict uRPF")

    applied = get_applied_interfaces(as_obj, scenario, sav_policy)

    # לפי DEFAULT_SAV_POLICY_INTERFACE_DICT, Strict uRPF = customer+peer
    assert as_obj.customer_asns in applied
    assert as_obj.peer_asns in applied
    assert as_obj.provider_asns not in applied


def test_get_applied_interfaces_override():
    as_obj = DummyAS()
    override = {
        "Strict uRPF": frozenset([Interfaces.PROVIDER.value])
    }
    scenario = SimpleNamespace(
        scenario_config=DummyScenarioConfig(override=override)
    )
    sav_policy = DummyPolicy("Strict uRPF")

    applied = get_applied_interfaces(as_obj, scenario, sav_policy)

    # כעת רק providers אמורים להיות מוחלים
    assert as_obj.provider_asns in applied
    assert as_obj.customer_asns not in applied
    assert as_obj.peer_asns not in applied
