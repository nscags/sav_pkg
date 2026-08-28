from pathlib import Path
from time import time
import random
import os

from bgpy.simulation_framework import Simulation
from sav_pkg.simulation_engine.sav_simulation_engine import SAVSimulationEngine
from bgpy.simulation_engine import BGPFull, ASRAFull, ASPAFull
from bgpy.shared.enums import ASGroups

from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.scenarios import SAVScenarioConfig, SAVScenario
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker
from sav_pkg.simulation_engine.policies.sav import (
    BAR_SAV_PI_PP_Alg_A,
    BAR_SAV_PI_PP_Alg_B,
)



def main():
    """

    """
    # Simulation for the paper
    random.seed(os.environ['JOB_COMPLETION_INDEX'], 0)
    sim = Simulation(
        SimulationEngineCls=SAVSimulationEngine,
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
                BaseSAVPolicyCls=BAR_SAV_PI_PP_Alg_A,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                num_attackers=0,
                scenario_label="alg_a_bgp",
            ),
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                BaseSAVPolicyCls=BAR_SAV_PI_PP_Alg_B,
                victim_subcategory_attr=ASGroups.MULTIHOMED.value,
                reflector_default_adopters=True,
                num_attackers=0,
                scenario_label="alg_b_bgp",
            ),
            # SAVScenarioConfig(
            #     ScenarioCls=SAVScenario,
            #     BasePolicyCls=ASPAFull,
            #     BaseSAVPolicyCls=BAR_SAV_PI_PP_Alg_A,
            #     victim_subcategory_attr=ASGroups.MULTIHOMED.value,
            #     reflector_default_adopters=True,
            #     num_attackers=0,
            #     scenario_label="alg_a_aspa",
            # ),
            # SAVScenarioConfig(
            #     ScenarioCls=SAVScenario,
            #     BasePolicyCls=ASPAFull,
            #     BaseSAVPolicyCls=BAR_SAV_PI_PP_Alg_B,
            #     victim_subcategory_attr=ASGroups.MULTIHOMED.value,
            #     reflector_default_adopters=True,
            #     num_attackers=0,
            #     scenario_label="alg_b_aspa",
            # ), 
            # SAVScenarioConfig(
            #     ScenarioCls=SAVScenario,
            #     BasePolicyCls=ASRAFull,
            #     BaseSAVPolicyCls=BAR_SAV_PI_PP_Alg_A,
            #     victim_subcategory_attr=ASGroups.MULTIHOMED.value,
            #     reflector_default_adopters=True,
            #     num_attackers=0,
            #     scenario_label="alg_a_asra",
            # ),
            # SAVScenarioConfig(
            #     ScenarioCls=SAVScenario,
            #     BasePolicyCls=ASRAFull,
            #     BaseSAVPolicyCls=BAR_SAV_PI_PP_Alg_B,
            #     victim_subcategory_attr=ASGroups.MULTIHOMED.value,
            #     reflector_default_adopters=True,
            #     num_attackers=0,
            #     scenario_label="alg_b_asra",
            # ),
        ),
        output_dir=Path(f"~/sav/results/bspi_pp/50t_fp_test").expanduser(),
        num_trials=50,
        parse_cpus=int(os.environ.get("SLURM_NTASKS")),
        ASGraphAnalyzerCls=SAVASGraphAnalyzer,
        GraphDataAggregatorCls=SAVMetricTracker,
    )
    sim.run()


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print(f"TOTAL RUNTIME: {end - start}")
