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
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_engine.policies.sav import (
    BAR_SAV_PI_PP,
)
from sav_pkg.simulation_engine.policies.sav.fp_urpf_pi import FeasiblePathuRPF_PI


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
                BaseSAVPolicyCls=FeasiblePathuRPF_PI,
                victim_default_adopters=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                num_reflectors=1,
                scenario_label="bgp",
            ),
        ),
        output_dir=Path(f"~/sav/results/1r_3t_e2a_fppi_test").expanduser(),
        num_trials=10,
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