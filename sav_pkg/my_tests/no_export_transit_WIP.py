import pytest
from sav_pkg.policies.bgp.bgp_noexport2some import BGPNoExport2Some
from sav_pkg.simulation_framework.scenarios.sav_scenario import SAVScenario
from sav_pkg.simulation_framework.scenarios.sav_scenario_config import SAVScenarioConfig
from bgpy.utils.engine_run_config import EngineRunConfig
from bgpy.tests.engine_tests.engine_test_configs.examples.as_graph_info_000 import (
    as_graph_info_000 as EX_CFG
)
from bgpy.simulation_framework.simulation import Simulation


def test_noexport_transit_basic():
    """
    This test checks that a Transit AS with no-export-to-some policy
    only exports announcements to the allowed subset of providers.
    """

    # Transit AS with multiple providers in example graph: AS 3 has providers [1, 2]
    transit_asn = 3

    # allowed provider subset (just AS 1)
    export_map = { transit_asn: [1] }

    sav_cfg = SAVScenarioConfig(
        ScenarioCls=SAVScenario,
        export_policy=export_map,
        PolicyCls=BGPNoExport2Some  # <- important!
    )

    cfg = EngineRunConfig(
        name="test_noexport_transit",
        desc="Testing no-export-to-some on a transit AS",
        scenario_config=sav_cfg,
        as_graph_info=EX_CFG.as_graph_info,
    )

    sim = Simulation(cfg)
    sim.parse_cpus = 1

    metric_tracker = sim.run()

    # sanity: simulation finished correctly
    assert metric_tracker is not None

    # Now we check if AS3 exported only to AS1 and not to AS2
    exports = metric_tracker.as_export_records.get(transit_asn, {})
    providers = list(exports.keys())

    assert 1 in providers, "Transit AS should export to provider AS1"
    assert 2 not in providers, "Transit AS should NOT export to provider AS2"
