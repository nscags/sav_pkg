from pathlib import Path
from time import time
import random

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGP, BGPFull
from bgpy.enums import ASGroups

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework import (
    SAVScenarioConfig, 
    SAVScenarioExport2Some,
    SAVASGraphAnalyzer, 
)
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.policies.sav import (
    # LooseuRPF,
    # StrictuRPF,
    # FeasiblePathuRPF,
    # EnhancedFeasiblePathuRPFAlgB,
    # EnhancedFeasiblePathuRPFAlgA,
    # EnhancedFeasiblePathuRPFAlgAwoPeers,
    # RFC8704,
    # BAR_SAV,
    BAR_SAV_Full,
)
from sav_pkg.policies.bgp import (
    BGPFullExport2Some,
)
from sav_pkg.utils.utils import get_metric_keys, get_export_to_some_dict


def main():
    # Simulation for the paper
    # random.seed(os.environ['JOB_COMPLETION_INDEX'])
    bgpfull_e2s_asn_cls_dict = get_export_to_some_dict(e2s_policy=BGPFullExport2Some)
    sim = Simulation(
        percent_adoptions = (
            1.0,
        ),
        scenario_configs=(
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioExport2Some,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_Full,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=10,
                scenario_label="bar_sav_full",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
        ),
        output_dir=Path(f"~/sav/results/10_2_val").expanduser(),
        num_trials=2,
        parse_cpus=1,
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