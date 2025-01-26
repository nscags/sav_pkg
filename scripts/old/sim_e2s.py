from pathlib import Path
from time import time
from multiprocessing import cpu_count

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGP, BGPFull

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sav_pkg.simulation_framework import (
    SAVScenarioConfig, 
    SAVScenario, 
    SAVScenarioCPPPercentAdoption,
    SAVASGraphAnalyzer, 
    MetricTracker
)
from sav_pkg.simulation_engine import (
    FeasiblePathuRPF, 
    StrictuRPF, 
    EnhancedFeasiblePathuRPFAlgB, 
    EnhancedFeasiblePathuRPFAlgA, 
    BAR_SAV, 
    RFC8704,
    LooseuRPF,
    BGPExport2Some,
    BGPFullExport2Some,
)
from sav_pkg.simulation_framework.utils import get_metric_keys


def main():
    # Simulation for the paper
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
                ScenarioCls=SAVScenarioCPPPercentAdoption,
                BasePolicyCls=BGP,
                AdoptPolicyCls=BGPExport2Some,
                special_percent_adoption = 0.4043,
                num_reflectors=10,
                BaseSAVPolicyCls=LooseuRPF,
                reflector_default_adopters=True,
                scenario_label="loose"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdoption,
                BasePolicyCls=BGP,
                AdoptPolicyCls=BGPExport2Some,
                special_percent_adoption = 0.4043,
                num_reflectors=10,
                BaseSAVPolicyCls=StrictuRPF,
                reflector_default_adopters=True,
                scenario_label="strict"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdoption,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullExport2Some,
                special_percent_adoption = 0.4043,
                num_reflectors=10,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                reflector_default_adopters=True,
                scenario_label="feasible"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdoption,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullExport2Some,
                special_percent_adoption = 0.4043,
                num_reflectors=10,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgB,
                reflector_default_adopters=True,
                scenario_label="enhanced"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdoption,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullExport2Some,
                special_percent_adoption = 0.4043,
                num_reflectors=10,
                BaseSAVPolicyCls=BAR_SAV,
                reflector_default_adopters=True,
                scenario_label="bar_sav"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdoption,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullExport2Some,
                special_percent_adoption = 0.4043,
                num_reflectors=10,
                BaseSAVPolicyCls=EnhancedFeasiblePathuRPFAlgA,
                reflector_default_adopters=True,
                scenario_label="efp_alg_a"
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioCPPPercentAdoption,
                BasePolicyCls=BGPFull,
                AdoptPolicyCls=BGPFullExport2Some,
                special_percent_adoption = 0.4043,
                num_reflectors=10,
                BaseSAVPolicyCls=RFC8704,
                reflector_default_adopters=True,
                scenario_label="rfc8704"
            ),
        ),
        output_dir=Path(f"~/sav/results/1_1_e2s").expanduser(),
        num_trials=100,
        parse_cpus=10,
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