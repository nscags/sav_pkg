from pathlib import Path
from time import time

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGPFull, ASPAFull

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework import (
    SAVScenarioConfig, 
    SAVScenario, 
    SAVScenarioCPPPercentAdoption,
    SAVASGraphAnalyzer, 
    MetricTracker,
)
from sav_pkg.simulation_engine import (
    BAR_SAV,
)
from sav_pkg.simulation_framework.utils import get_metric_keys
from sav_pkg.utils.utils import get_real_world_rov_asn_cls_dict


def main():
    # Simulation for the paper
    rov_dict = get_real_world_rov_asn_cls_dict()
    
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
                num_reflectors=10,
                BaseSAVPolicyCls=BAR_SAV,
                reflector_default_adopters=True,
                scenario_label="bar_sav_bgp"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                num_reflectors=10,
                BaseSAVPolicyCls=BAR_SAV,
                reflector_default_adopters=True,
                hardcoded_asn_cls_dict=rov_dict,
                scenario_label="bar_sav_rov"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdoption,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFull,
                special_percent_adoption = 0.1,
                num_reflectors=10,
                BaseSAVPolicyCls=BAR_SAV,
                reflector_default_adopters=True,
                scenario_label="bar_sav_aspa_10"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdoption,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFull,
                special_percent_adoption= 0.2,
                num_reflectors=10,
                BaseSAVPolicyCls=BAR_SAV,
                reflector_default_adopters=True,
                scenario_label="bar_sav_aspa_20"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdoption,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFull,
                special_percent_adoption = 0.5,
                num_reflectors=10,
                BaseSAVPolicyCls=BAR_SAV,
                reflector_default_adopters=True,
                scenario_label="bar_sav_aspa_50"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdoption,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFull,
                special_percent_adoption = 0.8,
                num_reflectors=10,
                BaseSAVPolicyCls=BAR_SAV,
                reflector_default_adopters=True,
                scenario_label="bar_sav_aspa_80"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdoption,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=ASPAFull,
                special_percent_adoption = 0.99,
                num_reflectors=10,
                BaseSAVPolicyCls=BAR_SAV,
                reflector_default_adopters=True,
                scenario_label="bar_sav_aspa_99"
            ),
        ),
        output_dir=Path(f"~/sav/results/50_10_bar_sav").expanduser(),
        num_trials=50,
        parse_cpus=2,
        ASGraphAnalyzerCls=SAVASGraphAnalyzer,
        MetricTrackerCls=MetricTracker,
        metric_keys=get_metric_keys(),
    )
    sim.run()


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print(f"TOTAL RUNTIME: {end - start}")