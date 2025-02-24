from pathlib import Path
from time import time
import random

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
    LooseuRPF,
    StrictuRPF,
    FeasiblePathuRPF,
    EnhancedFeasiblePathuRPFAlgB,
    EnhancedFeasiblePathuRPFAlgA,
    EnhancedFeasiblePathuRPFAlgAwPeers,
    RFC8704,
    BAR_SAV,
)
from sav_pkg.simulation_framework.utils import get_metric_keys

def main():
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
    sim = Simulation(
        percent_adoptions=(
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
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=LooseuRPF,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="loose"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=StrictuRPF,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="strict"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="feasible"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgB,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_b"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_a"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgAwPeers,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_a_w_peers"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=RFC8704,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="rfc8704"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav"
            ),
        ),
        output_dir=Path(f"~/sav/results/300_5_rda").expanduser(),
        num_trials=300,
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