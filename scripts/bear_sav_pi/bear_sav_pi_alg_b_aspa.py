from pathlib import Path
from time import time
import random
import os
import sys

from bgpy.simulation_framework import Simulation
from sav_pkg.simulation_engine.sav_simulation_engine import SAVSimulationEngine
from bgpy.simulation_engine import BGPFull, ASPAFull
from bgpy.shared.enums import ASGroups

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_engine.policies.sav import (
    BeAR_SAV_PI_B,
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
                BaseSAVPolicyCls=BeAR_SAV_PI_B,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                num_reflectors=5,
                reflector_default_adopters=True,
                scenario_label="aspa_0",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BeAR_SAV_PI_B,
                AdoptPolicyCls=ASPAFull,
                ctrl_plane_percent_adoption=0.1,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                num_reflectors=5,
                reflector_default_adopters=True,
                scenario_label="aspa_10",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BeAR_SAV_PI_B,
                AdoptPolicyCls=ASPAFull,
                ctrl_plane_percent_adoption=0.2,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                num_reflectors=5,
                reflector_default_adopters=True,
                scenario_label="aspa_20",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BeAR_SAV_PI_B,
                AdoptPolicyCls=ASPAFull,
                ctrl_plane_percent_adoption=0.5,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                num_reflectors=5,
                reflector_default_adopters=True,
                scenario_label="aspa_50",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BeAR_SAV_PI_B,
                AdoptPolicyCls=ASPAFull,
                ctrl_plane_percent_adoption=0.8,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                num_reflectors=5,
                reflector_default_adopters=True,
                scenario_label="aspa_80",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BeAR_SAV_PI_B,
                AdoptPolicyCls=ASPAFull,
                ctrl_plane_percent_adoption=0.99,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                num_reflectors=5,
                reflector_default_adopters=True,
                scenario_label="aspa_99",
            ),
        ),
        output_dir=Path(f"~/sav/results/bear_sav_pi/base/5r_100t_e2a_alg_b_aspa").expanduser(),
        num_trials=100,
        parse_cpus=int(os.environ.get("SLURM_NTASKS")),
        ASGraphAnalyzerCls=SAVASGraphAnalyzer,
        GraphDataAggregatorCls=SAVMetricTracker,
    )
    sim.run()


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print(f"TOTAL RUNTIME: {end - start}")