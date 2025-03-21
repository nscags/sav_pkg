from pathlib import Path
from time import time
import random

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGPFull, ASPAFull

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework import (
    SAVScenarioConfig, 
    SAVScenarioASPAExport2Some,
    SAVASGraphAnalyzer, 
)
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.policies import (
    RefinedAlgA,
    BGPFullExport2Some,
)
from sav_pkg.utils.utils import get_metric_keys, get_export_to_some_dict


def main():
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
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
                ScenarioCls=SAVScenarioASPAExport2Some,
                BasePolicyCls=BGPFull,
                num_reflectors=5,
                BaseSAVPolicyCls=RefinedAlgA,
                reflector_default_adopters=True,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="refined_alg_a_aspa_0",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioASPAExport2Some,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFull,
                special_percent_adoption = 0.1,
                num_reflectors=5,
                BaseSAVPolicyCls=RefinedAlgA,
                reflector_default_adopters=True,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="refined_alg_a_aspa_10"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioASPAExport2Some,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFull,
                special_percent_adoption= 0.2,
                num_reflectors=5,
                BaseSAVPolicyCls=RefinedAlgA,
                reflector_default_adopters=True,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="refined_alg_a_aspa_20"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioASPAExport2Some,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFull,
                special_percent_adoption = 0.5,
                num_reflectors=5,
                BaseSAVPolicyCls=RefinedAlgA,
                reflector_default_adopters=True,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="refined_alg_a_aspa_50"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioASPAExport2Some,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFull,
                special_percent_adoption = 0.8,
                num_reflectors=5,
                BaseSAVPolicyCls=RefinedAlgA,
                reflector_default_adopters=True,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="refined_alg_a_aspa_80"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioASPAExport2Some,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFull,
                special_percent_adoption = 0.99,
                num_reflectors=5,
                BaseSAVPolicyCls=RefinedAlgA,
                reflector_default_adopters=True,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="refined_alg_a_aspa_99"
            ),
        ),
        output_dir=Path(f"~/sav/results/300_5_aspa_e2s").expanduser(),
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