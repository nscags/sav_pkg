from pathlib import Path
from time import time
from datetime import date
from frozendict import frozendict
import random
import os
import sys

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGP, BGPFull, ASPA, ASPAFull
from bgpy.enums import ASGroups

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework import (
    SAVScenarioConfig, 
    SAVScenario,
    SAVASGraphAnalyzer, 
)
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.policies import (
    BAR_SAV_PI,
    LooseuRPF,
    BGPExport2Some,
    BGPFullExport2Some,
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
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PI,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa0",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=LooseuRPF,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="loose_aspa0",
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PI,
                AdoptPolicyCls=ASPAFull,
                ctrl_plane_percent_adoption=0.1,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa10",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=LooseuRPF,
                AdoptPolicyCls=ASPA,
                ctrl_plane_percent_adoption=0.1,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="loose_aspa10",
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PI,
                AdoptPolicyCls=ASPAFull,
                ctrl_plane_percent_adoption=0.2,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa20",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=LooseuRPF,
                AdoptPolicyCls=ASPA,
                ctrl_plane_percent_adoption=0.2,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="loose_aspa20",
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PI,
                AdoptPolicyCls=ASPAFull,
                ctrl_plane_percent_adoption=0.5,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa50",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=LooseuRPF,
                AdoptPolicyCls=ASPA,
                ctrl_plane_percent_adoption=0.5,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="loose_aspa50",
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PI,
                AdoptPolicyCls=ASPAFull,
                ctrl_plane_percent_adoption=0.8,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa80",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=LooseuRPF,
                AdoptPolicyCls=ASPA,
                ctrl_plane_percent_adoption=0.8,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="loose_aspa80",
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PI,
                AdoptPolicyCls=ASPAFull,
                ctrl_plane_percent_adoption=0.99,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa99",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=LooseuRPF,
                AdoptPolicyCls=ASPA,
                ctrl_plane_percent_adoption=0.99,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="loose_aspa99",
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict,
            ),
        ),
        output_dir=Path(f"~/sav/results/5r_100t_te_bspi").expanduser(),
        num_trials=100,
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