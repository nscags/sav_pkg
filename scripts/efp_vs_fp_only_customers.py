from pathlib import Path
from time import time
from multiprocessing import cpu_count

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGP, BGPFull

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework import SAVScenarioConfig, SAVScenario, SAVASGraphAnalyzer, MetricTracker
from sav_pkg.simulation_engine import FeasiblePathuRPF, StrictuRPF, EnhancedFeasiblePathuRPF, BAR_SAV, FeasiblePathuRPFOnlyCustomers
from sav_pkg.simulation_framework.utils import get_metric_keys


def main():
    # Simulation for the paper
    sim = Simulation(
        percent_adoptions = (
            0.0,
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            0.9,
            0.99,
        ),
        scenario_configs=(
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                num_reflectors=10,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                reflector_default_adopters=True,
                scenario_label="feasible"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                num_reflectors=10,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPF,
                reflector_default_adopters=True,
                scenario_label="enhanced"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                num_reflectors=10,
                BaseSAVPolicyCls=FeasiblePathuRPFOnlyCustomers,
                reflector_default_adopters=True,
                scenario_label="fpOnlyCustomers"
            ),
        ),
        output_dir=Path(f"~/sav/efpvsfp_results").expanduser(),
        num_trials=99,
        parse_cpus=8,
        ASGraphAnalyzerCls=SAVASGraphAnalyzer,
        MetricTrackerCls=MetricTracker,
        metric_keys=get_metric_keys(),
    )
    sim.run()


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print(f"TOTAL RUNTIME: {end - start}")