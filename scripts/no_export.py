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
    SAVScenario,
    SAVScenarioNoExport2Some,
    SAVASGraphAnalyzer, 
)
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.policies import (
    LooseuRPF,
    StrictuRPF,
    FeasiblePathuRPF,
    EnhancedFeasiblePathuRPFAlgB,
    EnhancedFeasiblePathuRPFAlgA,
    EnhancedFeasiblePathuRPFAlgAwoPeers,
    RFC8704,
    BAR_SAV,
    BAR_SAV_Full,
    BGPNoExport2Some,
    BGPFullNoExport2Some,
    ASPAFullNoExport2Some,
)
from sav_pkg.enums import Interfaces
from sav_pkg.utils.utils import get_metric_keys


def main():
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'])
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
                AdoptPolicyCls=BGPNoExport2Some, # victims default adopters
                victim_default_adopters=True,
                BaseSAVPolicyCls=LooseuRPF,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value, # victims must be multihomed
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, # attackers must be multihomed
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="loose",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGP,
                AdoptPolicyCls=BGPNoExport2Some,
                victim_default_adopters=True,
                BaseSAVPolicyCls=StrictuRPF,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="strict",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGP,
                AdoptPolicyCls=BGPNoExport2Some,
                victim_default_adopters=True,
                BaseSAVPolicyCls=StrictuRPF,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="strict_otc",
                override_default_interface_dict=frozendict({
                    "Strict uRPF": (Interfaces.CUSTOMER.value,),
                }),
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullNoExport2Some,
                victim_default_adopters=True,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="feasible",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullNoExport2Some,
                victim_default_adopters=True,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="feasible_wo_providers",
                override_default_interface_dict=frozendict({
                    "Feasible-Path uRPF": (Interfaces.CUSTOMER.value, Interfaces.PEER.value),
                }),
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullNoExport2Some,
                victim_default_adopters=True,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="feasible_otc",
                override_default_interface_dict=frozendict({
                    "Feasible-Path uRPF": (Interfaces.CUSTOMER.value,),
                }),
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullNoExport2Some,
                victim_default_adopters=True,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgB,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_b",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullNoExport2Some,
                victim_default_adopters=True,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_a",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullNoExport2Some,
                victim_default_adopters=True,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgAwoPeers,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="efp_alg_a_wo_peers",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullNoExport2Some,
                victim_default_adopters=True,
                BaseSAVPolicyCls=BAR_SAV,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFullNoExport2Some,
                victim_default_adopters=True,
                BaseSAVPolicyCls=BAR_SAV,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                victim_providers_ann=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullNoExport2Some,
                victim_default_adopters=True,
                BaseSAVPolicyCls=BAR_SAV_Full,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_full",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFullNoExport2Some,
                victim_default_adopters=True,
                BaseSAVPolicyCls=BAR_SAV_Full,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                victim_providers_ann=True,
                num_reflectors=5,
                scenario_label="bar_sav_full_aspa",
            ),
        ),
        output_dir=Path(f"~/sav/results/5_100_no_export").expanduser(),
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