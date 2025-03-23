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
    SAVScenarioCPPPercentAdopt,
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
from sav_pkg.policies.bgp import BGPExport2Some, BGPFullExport2Some
from sav_pkg.utils.utils import get_metric_keys, get_export_to_some_dict


def main():
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
    bgp_e2s_asn_cls_dict = get_export_to_some_dict(e2s_policy=BGPExport2Some)
    bgpfull_e2s_asn_cls_dict = get_export_to_some_dict(e2s_policy=BGPFullExport2Some)
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
                ScenarioCls=SAVScenarioCPPPercentAdopt,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=LooseuRPF,
                AdoptPolicyCls=BGPExport2Some,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="loose",
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdopt,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=StrictuRPF,
                AdoptPolicyCls=BGPExport2Some,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="strict",
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdopt,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                AdoptPolicyCls=BGPFullExport2Some,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="feasible",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdopt,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgB,
                AdoptPolicyCls=BGPFullExport2Some,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_b",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdopt,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA,
                AdoptPolicyCls=BGPFullExport2Some,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_a",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdopt,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgAwoPeers,
                AdoptPolicyCls=BGPFullExport2Some,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_a_wo_peers",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdopt,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=RFC8704,
                AdoptPolicyCls=BGPFullExport2Some,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="rfc8704",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdopt,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=RefinedAlgA,
                AdoptPolicyCls=BGPFullExport2Some,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="refined_alg_a",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict
            ),
        ),
        output_dir=Path(f"~/sav/results/1000_5_rda_e2s").expanduser(),
        num_trials=1000,
        parse_cpus=20,
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