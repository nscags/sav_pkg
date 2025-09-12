from pathlib import Path
from time import time
import random
from frozendict import frozendict

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGP, BGPFull
from bgpy.enums import ASGroups

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework import (
    SAVScenarioConfig, 
    SAVScenarioDSR,
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
    BAR_SAV,
    BAR_SAV_Full,
)
from sav_pkg.policies.bgp import (
    BGPExport2Some,
    BGPFullExport2Some,
)
from sav_pkg.enums import Prefixes, Interfaces
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
            # SAVScenarioConfig(
            #     ScenarioCls=SAVScenarioDSR,
            #     BasePolicyCls=BGP,
            #     BaseSAVPolicyCls=LooseuRPF,
            #     num_attackers=0,
            #     num_users=5,
            #     source_prefix=Prefixes.ANYCAST_SERVER.value,
            #     anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
            #     edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
            #     hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict,
            #     scenario_label="loose",
            # ),
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
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=StrictuRPF,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict,
                scenario_label="strict_otc",
                override_default_interface_dict=frozendict({
                    "Strict uRPF": (Interfaces.CUSTOMER.value,),
                }),
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
                BaseSAVPolicyCls=FeasiblePathuRPF,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="feasible_wo_providers",
                override_default_interface_dict=frozendict({
                    "Feasible-Path uRPF": (Interfaces.CUSTOMER.value, Interfaces.PEER.value),
                }),
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
                scenario_label="feasible_otc",
                override_default_interface_dict=frozendict({
                    "Feasible-Path uRPF": (Interfaces.CUSTOMER.value,),
                }),
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="efp_alg_a",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgAwoPeers,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="efp_alg_a_wo_peers",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioDSR,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgB,
                num_attackers=0,
                num_users=5,
                source_prefix=Prefixes.ANYCAST_SERVER.value,
                anycast_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                edge_server_subcategory_attr=ASGroups.MULTIHOMED.value,
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                scenario_label="efp_alg_b",
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
                BaseSAVPolicyCls=BAR_SAV_Full,
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
                BaseSAVPolicyCls=BAR_SAV_Full,
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
        output_dir=Path(f"~/sav/results/5_500_dsr").expanduser(),
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