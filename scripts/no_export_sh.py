from pathlib import Path
from time import time
import random
import os
import sys
from frozendict import frozendict
from datetime import date

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGP, BGPFull
from bgpy.enums import ASGroups

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.policies.sav import (
    StrictuRPF,
    FeasiblePathuRPF,
    FeasiblePathuRPF_OTC,
    FeasiblePathuRPF_All,
    EFP_A,
    EFP_A_wPeers,
    EFP_B,
    BAR_SAV,
    BAR_SAV_wBSPI,
)
from sav_pkg.policies.bgp import (
    BGPExport2Some,
    BGPFullExport2Some,
)
from sav_pkg.policies.aspa import ASPAFullExport2Some
from sav_pkg.utils.utils import get_metric_keys, get_traffic_engineering_behavior_asn_cls_dict
from sav_pkg.enums import Interfaces


def main():
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
    bgp_e2s_asn_cls_dict = get_traffic_engineering_behavior_asn_cls_dict(
        export_policy=BGPExport2Some,
        traffic_engineering_subcategory="no-export",
    )
    bgpfull_e2s_asn_cls_dict = get_traffic_engineering_behavior_asn_cls_dict(
        export_policy=BGPFullExport2Some,
        traffic_engineering_subcategory="no-export",
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
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
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
                BaseSAVPolicyCls=FeasiblePathuRPF_OTC,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="feasible_otc",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                attacker_broadcast=False,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=FeasiblePathuRPF_All,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="feasible_all",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                attacker_broadcast=False,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EFP_A,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
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
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
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
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
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
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
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
                scenario_label="bar_sav_aspa",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                attacker_broadcast=False,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_wBSPI,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
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
                attacker_broadcast=False,
            ),
        ),
        output_dir=Path(f"~/sav/results/5r_1000t_ne_sh").expanduser(),
        num_trials=1000,
        parse_cpus=40,
        ASGraphAnalyzerCls=SAVASGraphAnalyzer,
        MetricTrackerCls=SAVMetricTracker,
        metric_keys=get_metric_keys(),
        as_graph_constructor_kwargs=frozendict(
            {
                "as_graph_collector_kwargs": frozendict({
                        "dl_time": date(2025, 9, 1),
                })
            }
        )
    )
    sim.run()


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print(f"TOTAL RUNTIME: {end - start}")