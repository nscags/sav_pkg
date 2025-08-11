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
    SAVScenario,
    SAVScenarioNoExport2Some,
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
from sav_pkg.policies.bgp import BGPNoExport2Some, BGPFullNoExport2Some
from sav_pkg.policies.aspa import ASPAFullNoExport2Some
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
                BaseSAVPolicyCls=StrictuRPF,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="strict",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullNoExport2Some,
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
                BaseSAVPolicyCls=RFC8704,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="rfc8704",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullNoExport2Some,
                BaseSAVPolicyCls=BAR_SAV,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioNoExport2Some,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFullNoExport2Some,
                BaseSAVPolicyCls=BAR_SAV,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_aspa_provider_ann",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullNoExport2Some,
                BaseSAVPolicyCls=BAR_SAV_Full,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_full",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioNoExport2Some,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFullNoExport2Some,
                BaseSAVPolicyCls=BAR_SAV_Full,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                attacker_subcategory_attr=ASGroups.MULTIHOMED.value, 
                reflector_default_adopters=True,
                num_reflectors=5,
                scenario_label="bar_sav_full_aspa_provider_ann",
            ),
        ),
        output_dir=Path(f"~/sav/results/5_500_no_e2s").expanduser(),
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