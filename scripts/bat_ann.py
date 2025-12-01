from pathlib import Path
from time import time
import random
import os
import sys
from frozendict import frozendict
from datetime import date

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGPFull
from bgpy.enums import ASGroups

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig, 
    SAVScenarioBATAnn,
)
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.policies import (
    BAR_SAV,
    ASPAFullNoExport2Some,
)
from sav_pkg.utils.utils import get_metric_keys, get_traffic_engineering_behavior_asn_cls_dict


def main():
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
    bgpfull_e2s_asn_cls_dict = get_traffic_engineering_behavior_asn_cls_dict(
        export_policy=ASPAFullNoExport2Some,
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
                ScenarioCls=SAVScenarioBATAnn,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                victim_providers_ann=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa0",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioBATAnn,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                ctrl_plane_percent_adoption=0.1,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                victim_providers_ann=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa10",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioBATAnn,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                ctrl_plane_percent_adoption=0.2,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                victim_providers_ann=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa20",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioBATAnn,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                ctrl_plane_percent_adoption=0.5,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                victim_providers_ann=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa50",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioBATAnn,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                ctrl_plane_percent_adoption=0.8,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                victim_providers_ann=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa80",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioBATAnn,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                ctrl_plane_percent_adoption=0.99,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                victim_providers_ann=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa99",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
        ),
        output_dir=Path(f"~/sav/results/5r_100t_bat_ann").expanduser(),
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