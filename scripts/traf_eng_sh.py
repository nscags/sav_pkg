from pathlib import Path
from time import time
import random
import os
import sys

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGPFull, BGP
from bgpy.enums import ASGroups

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework import (
    SAVScenarioConfig, 
    SAVScenario,
    SAVASGraphAnalyzer, 
)
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.policies import (
    StrictuRPF,
    FeasiblePathuRPF,
    EFP_A,
    EFP_A_wPeers,
    EFP_B,
    BAR_SAV,
    BAR_SAV_wBSPI,
    BGPExport2Some,
    BGPFullExport2Some,
    ASPAFullExport2Some,
)
from sav_pkg.utils.utils import get_metric_keys, get_traffic_engineering_behavior_asn_cls_dict


def main():
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
    bgp_e2s_asn_cls_dict = get_traffic_engineering_behavior_asn_cls_dict(
        export_policy=BGPExport2Some,
    )
    bgpfull_e2s_asn_cls_dict = get_traffic_engineering_behavior_asn_cls_dict(
        export_policy=BGPFullExport2Some,
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
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=StrictuRPF,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="strict",
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict,
                attacker_broadcast=False,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="feasible",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                attacker_broadcast=False,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EFP_A,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_a",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                attacker_broadcast=False,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EFP_A_wPeers,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_a_w_peers",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                attacker_broadcast=False,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EFP_B,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_b",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                attacker_broadcast=False,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                attacker_broadcast=False,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                AdoptPolicyCls=ASPAFullExport2Some,
                victim_default_adopters=True,
                victim_providers_ann=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_full_aspa",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_wBSPI,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_full",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                attacker_broadcast=False,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_wBSPI,
                AdoptPolicyCls=ASPAFullExport2Some,
                victim_default_adopters=True,
                victim_providers_ann=True,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_full_aspa",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
        ),
        output_dir=Path(f"~/sav/results/5r_100t_te_sh").expanduser(),
        num_trials=100,
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