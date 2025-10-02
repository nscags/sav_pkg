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
from sav_pkg.policies.sav import (
    BAR_SAV,
)
from sav_pkg.policies.bgp import (
    BGPFullExport2Some,
)
from sav_pkg.utils.utils import get_metric_keys, get_traffic_engineering_behavior_asn_cls_dict


def main():
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
    # bgpfull_e2a_asn_cls_dict = get_traffic_engineering_behavior_asn_cls_dict(
    #     export_policy=BGPFullExport2Some,
    #     traffic_engineering_subcategory="export-to-all"
    # )
    bgpfull_e2s_asn_cls_dict = get_traffic_engineering_behavior_asn_cls_dict(
        export_policy=BGPFullExport2Some,
        traffic_engineering_subcategory="export-to-some"
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
            # SAVScenarioConfig(
            #     ScenarioCls=SAVScenario,
            #     BasePolicyCls=BGPFull,
            #     BaseSAVPolicyCls=BAR_SAV,
            #     victim_subcategory_attr=ASGroups.MULTIHOMED.value,
            #     attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
            #     reflector_default_adopters=True,
            #     num_attackers=0,
            #     num_reflectors=5,
            #     scenario_label="bar_sav_e2a",
            #     hardcoded_asn_cls_dict=bgpfull_e2a_asn_cls_dict,
            # ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_attackers=0,
                num_reflectors=5,
                scenario_label="bar_sav_e2s",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
        ),
        output_dir=Path(f"~/sav/results/bar_sav_fp_e2s_c_100").expanduser(),
        num_trials=100,
        parse_cpus=50,
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