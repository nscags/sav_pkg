from pathlib import Path
from time import time
import random
import os
import sys

from bgpy.simulation_framework import Simulation
from sav_pkg.simulation_engine.sav_simulation_engine import SAVSimulationEngine
from bgpy.simulation_engine import BGPFull, ASRAFull
from bgpy.shared.enums import ASGroups

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_engine.policies.sav import (
    BAR_SAV_PP_wBSPI_PP,
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
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PP_wBSPI_PP,
                AdoptPolicyCls=ASRAFull,
                ctrl_plane_percent_adoption=0,
                victim_default_adopters=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                num_reflectors=1,
                scenario_label="asra_0",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PP_wBSPI_PP,
                AdoptPolicyCls=ASRAFull,
                ctrl_plane_percent_adoption=0.1,
                victim_default_adopters=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                num_reflectors=1,
                scenario_label="asra_10",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PP_wBSPI_PP,
                AdoptPolicyCls=ASRAFull,
                ctrl_plane_percent_adoption=0.2,
                victim_default_adopters=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                num_reflectors=1,
                scenario_label="asra_20",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PP_wBSPI_PP,
                AdoptPolicyCls=ASRAFull,
                ctrl_plane_percent_adoption=0.5,
                victim_default_adopters=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                num_reflectors=1,
                scenario_label="asra_50",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PP_wBSPI_PP,
                AdoptPolicyCls=ASRAFull,
                ctrl_plane_percent_adoption=0.8,
                victim_default_adopters=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                num_reflectors=1,
                scenario_label="asra_80",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PP_wBSPI_PP,
                AdoptPolicyCls=ASRAFull,
                ctrl_plane_percent_adoption=0.99,
                victim_default_adopters=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                num_reflectors=1,
                scenario_label="asra_99",
            ),
        ),
        output_dir=Path(f"~/sav/results/5r_100t_e2a_bspp_asra").expanduser(),
        num_trials=100,
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