from pathlib import Path
from time import time
import random
import os
import sys

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGP, BGPFull
from bgpy.enums import ASGroups

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework import (
    SAVScenarioConfig, 
    SAVScenarioDSR,
    SAVASGraphAnalyzer, 
)
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.policies.sav import (
    StrictuRPF,
    FeasiblePathuRPF,
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
from sav_pkg.enums import Prefixes
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
                ScenarioCls=SAVScenarioDSR,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=StrictuRPF,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict,
                scenario_label="strict",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="feasible",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EFP_A,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="efp_a",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EFP_A_wPeers,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="efp_a_w_peers",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EFP_B,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="efp_b",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="bar_sav",
            ),            
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                source_prefix_roa=True,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="bar_sav_roa",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_wBSPI,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="bar_sav_full",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_wBSPI,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                source_prefix_roa=True,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="bar_sav_full_roa",
            ),
        ),
        output_dir=Path(f"~/sav/results/5r_100t_dsr").expanduser(),
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