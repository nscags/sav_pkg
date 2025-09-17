from pathlib import Path
from time import time
import random

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGPFull
from bgpy.enums import ASGroups

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework import (
    SAVScenarioConfig, 
    SAVScenario,
    SAVASGraphAnalyzer, 
)
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.policies import (
    BAR_SAV_Full,
    BGPFullExport2Some,
    ASPAFullExport2Some,
)
from sav_pkg.utils.utils import get_metric_keys, get_traffic_engineering_behavior_asn_cls_dict


def main():
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
    bgpfull_e2s_asn_cls_dict_te = get_traffic_engineering_behavior_asn_cls_dict(
        export_policy=BGPFullExport2Some,
        path_prepending=False,
    )
    bgpfull_e2s_asn_cls_dict_e2s = get_traffic_engineering_behavior_asn_cls_dict(
        export_policy=BGPFullExport2Some,
        traffic_engineering_subcategory="export-to-some",
        path_prepending=False,
    )
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
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_Full,
                AdoptPolicyCls=ASPAFullExport2Some,
                victim_default_adopters=True,
                victim_providers_ann=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_full_aspa_te",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict_te,
                attacker_broadcast=False,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_Full,
                AdoptPolicyCls=ASPAFullExport2Some,
                victim_default_adopters=True,
                victim_providers_ann=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_full_aspa_e2s",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict_e2s,
                attacker_broadcast=False,
            ),
        ),
        output_dir=Path(f"~/sav/results/5_500_aspa").expanduser(),
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