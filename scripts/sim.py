from pathlib import Path
from time import time
from multiprocessing import cpu_count

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGP, BGPFull

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework import (
    SAVScenarioConfig, 
    SAVScenario, 
    SAVASGraphAnalyzer, 
    MetricTracker
)
from sav_pkg.simulation_engine import (
    FeasiblePathuRPF, 
    StrictuRPF, 
    EnhancedFeasiblePathuRPF, 
    BAR_SAV, 
    EnhancedFeasiblePathuRPFAlgA, 
    FeasiblePathuRPFOnlyCustomers, 
    RFC8704,
    LooseuRPF,
)
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
                BasePolicyCls=BGP,
                num_reflectors=10,
                BaseSAVPolicyCls=LooseuRPF,
                reflector_default_adopters=True,
                scenario_label="loose"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGP,
                num_reflectors=10,
                BaseSAVPolicyCls=StrictuRPF,
                reflector_default_adopters=True,
                scenario_label="strict"
            ),
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
                BaseSAVPolicyCls=BAR_SAV,
                reflector_default_adopters=True,
                scenario_label="bar_sav"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                num_reflectors=10,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA,
                reflector_default_adopters=True,
                scenario_label="efp_alg_a"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                num_reflectors=10,
                BaseSAVPolicyCls=FeasiblePathuRPFOnlyCustomers,
                reflector_default_adopters=True,
                scenario_label="fp_only_customers"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                num_reflectors=10,
                BaseSAVPolicyCls=RFC8704,
                reflector_default_adopters=True,
                scenario_label="rfc8704"
            ),
        ),
        output_dir=Path(f"~/sav/results").expanduser(),
        num_trials=100,
        parse_cpus=10,
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