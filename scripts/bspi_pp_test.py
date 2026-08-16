from pathlib import Path
from time import time
import random
import os
import sys

from bgpy.simulation_framework import Simulation
from sav_pkg.simulation_engine.sav_simulation_engine import SAVSimulationEngine
from bgpy.simulation_engine import BGPFull, ASRAFull, ASPAFull
from bgpy.shared.enums import ASGroups

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenarioKnownPeers
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_engine.policies.sav import (
    BAR_SAV_PI_PP,
)

def main():
    """

    """
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
    sim = Simulation(
        SimulationEngineCls=SAVSimulationEngine,
        percent_adoptions = (
            0.0,
            0.1,
            0.2,
            0.5,
            0.8,
            0.99,
        ),
        scenario_configs=(
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioKnownPeers,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PI_PP,
                victim_default_adopters=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                num_reflectors=1,
                scenario_label="bgp",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioKnownPeers,
                BasePolicyCls=ASRAFull,
                BaseSAVPolicyCls=BAR_SAV_PI_PP,
                victim_default_adopters=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                reflector_subcategory_attr=ASGroups.MULTIHOMED.value,
                num_reflectors=1,
                scenario_label="asra",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioKnownPeers,
                BasePolicyCls=ASPAFull,
                BaseSAVPolicyCls=BAR_SAV_PI_PP,
                victim_default_adopters=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                reflector_subcategory_attr=ASGroups.MULTIHOMED.value,
                num_reflectors=1,
                scenario_label="aspa",
            ),
        ),
        output_dir=Path(f"~/sav/results/1r_5t_e2a_bspi_pp_test_9").expanduser(),
        num_trials=5,
        parse_cpus=20,
        ASGraphAnalyzerCls=SAVASGraphAnalyzer,
        GraphDataAggregatorCls=SAVMetricTracker,
    )
    sim.run()


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print(f"TOTAL RUNTIME: {end - start}")
