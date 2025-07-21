from pathlib import Path
from time import time
import random

from bgpy.simulation_framework import Simulation, GraphFactory
from bgpy.simulation_engine import BGP, BGPFull

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework import (
    SAVScenarioConfig, 
    SAVScenarioDSR,
    SAVASGraphAnalyzer, 
)
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.policies.sav import (
    LooseuRPF,
    StrictuRPF,
    FeasiblePathuRPF,
    EnhancedFeasiblePathuRPFAlgB,
    EnhancedFeasiblePathuRPFAlgA,
    EnhancedFeasiblePathuRPFAlgAwoPeers,
    RFC8704,
    RefinedAlgA,
    BAR_SAV_PI,
    BAR_SAV_Full,
)
from sav_pkg.enums import Prefixes
from sav_pkg.utils.utils import get_metric_keys


def main():
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
    sim = Simulation(
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
                ScenarioCls=SAVScenarioDSR,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=LooseuRPF,
                scenario_label="loose",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=StrictuRPF,
                scenario_label="strict",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                scenario_label="feasible",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgB,
                scenario_label="efp_alg_b",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA,
                scenario_label="efp_alg_a",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgAwoPeers,
                scenario_label="efp_alg_a_wo_peers",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=RFC8704,
                scenario_label="rfc8704",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=RefinedAlgA,
                scenario_label="refined_alg_a",
            ),            
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                source_prefix_roa=True,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=RefinedAlgA,
                scenario_label="bar_sav",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                num_attackers=0,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                source_prefix_roa=True,
                num_users=5,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PI,
                scenario_label="bar_sav_pi",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                num_attackers=0,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                source_prefix_roa=True,
                num_users=5,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_Full,
                scenario_label="bar_sav_full",
            ),
        ),
        output_dir=Path(f"~/sav/results/5_500_dsr").expanduser(),
        num_trials=500,
        parse_cpus=40,
        ASGraphAnalyzerCls=SAVASGraphAnalyzer,
        MetricTrackerCls=SAVMetricTracker,
        metric_keys=get_metric_keys(),
    )
    sim.run()


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print(f"TOTAL RUNTIME: {end - start}")