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
    SAVScenarioExport2Some,
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
    RFC8704,
    BAR_SAV,
    BAR_SAV_Full,
)
from sav_pkg.policies.bgp import (
    BGPExport2Some,
    BGPFullExport2Some,
)
from sav_pkg.enums import Interfaces
from sav_pkg.utils.utils import get_metric_keys, get_export_to_some_dict


def main():
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
    bgp_e2s_asn_cls_dict = get_export_to_some_dict(e2s_policy=BGPExport2Some)
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
                ScenarioCls=SAVScenarioExport2Some,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=LooseuRPF,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="loose",
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioExport2Some,
                BasePolicyCls=BGP,
                BaseSAVPolicyCls=StrictuRPF,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="strict",
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioExport2Some,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="feasible",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioExport2Some,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="feasible_wo_providers",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
                override_default_interface_dict=frozendict({
                    "Feasible-Path uRPF": (Interfaces.CUSTOMER.value, Interfaces.PEER.value),
                }),
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioExport2Some,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgB,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_b",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioExport2Some,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_a",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioExport2Some,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgAwoPeers,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_a_wo_peers",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            # SAVScenarioConfig(
            #     ScenarioCls=SAVScenarioExport2Some,
            #     BasePolicyCls=BGPFull,
            #     BaseSAVPolicyCls=RFC8704,
            #     attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
            #     reflector_default_adopters=True,
            #     num_reflectors=5,
            #     scenario_label="rfc8704",
            #     hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            # ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioExport2Some,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioExport2Some,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_Full,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_full",
                hardcoded_asn_cls_dict=bgpfull_e2s_asn_cls_dict,
            ),
        ),
        output_dir=Path(f"~/sav/results/5_500_e2s").expanduser(),
        num_trials=500,
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