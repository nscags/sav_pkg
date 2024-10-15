from pathlib import Path

from bgpy.simulation_framework import Simulation
from bgpy.simulation_engine import BGPFull

from sav_pkg.simulation_framework import SAVScenarioConfig, SAVScenario, SAVASGraphAnalyzer, MetricTracker
from sav_pkg.simulation_engine import FeasiblePathuRPF
from sav_pkg.simulation_framework.utils import get_metric_key


def test_main():
    # Simulation for the paper
    sim = Simulation(
        percent_adoptions=(
            0.0,
        ),
        scenario_configs=(
            SAVScenarioConfig(
                ScenarioCls=SAVScenario,
                BasePolicyCls=BGPFull,
                num_reflectors=100,
                BaseSAVPolicyCls=FeasiblePathuRPF,
                reflector_default_adopters=True,
            ),
        ),
        output_dir=Path("C:\\Users\\njsca\\BGPResearch\SAV\\simulation_results"), # this I don't think works
        num_trials=100,
        parse_cpus=1, # try mulitple CPUs and see what happens (expecting some sort of error)
                      # need to implement the add function in MetricTracker
                      # or just steal Justin's
        ASGraphAnalyzerCls=SAVASGraphAnalyzer,
        MetricTrackerCls=MetricTracker,
        metric_keys=get_metric_key(),
    )
    sim.run()


if __name__ == '__main__':
    test_main()