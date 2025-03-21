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
)
from sav_pkg.policies.bgp import BGPFullExport2SomePathPrepending
from sav_pkg.utils.utils import get_metric_keys, get_export_to_some_dict


def main():
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
    e2s_asn_cls_dict = get_export_to_some_dict(e2s_policy=BGPFullExport2SomePathPrepending)
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
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=LooseuRPF,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="loose",
                hardcoded_asn_cls_dict=e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=StrictuRPF,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="strict",
                hardcoded_asn_cls_dict=e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="feasible",
                hardcoded_asn_cls_dict=e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgB,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_b",
                hardcoded_asn_cls_dict=e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_a",
                hardcoded_asn_cls_dict=e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgAwoPeers,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_a_wo_peers",
                hardcoded_asn_cls_dict=e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=RFC8704,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="rfc8704",
                hardcoded_asn_cls_dict=e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=RefinedAlgA,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="refined_alg_a",
                hardcoded_asn_cls_dict=e2s_asn_cls_dict
            ),
        ),
        output_dir=Path(f"~/sav/results/300_5_rda_e2s_pp").expanduser(),
        num_trials=300,
        parse_cpus=10,
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