import argparse
import os
import random
from time import time

from bgpy.simulation_framework import Simulation

from sav_pkg.simulation_engine.sav_simulation_engine import SAVSimulationEngine
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker

from matrix import MATRIX, NUM_TRIALS, build_scenario_configs, output_dir


def get_index() -> int:
    if "SLURM_ARRAY_TASK_ID" in os.environ:
        return int(os.environ["SLURM_ARRAY_TASK_ID"])
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=int, required=True)
    return parser.parse_args().index


def main():
    index = get_index()
    combo = MATRIX[index]
    print(f"Running matrix index {index}: {combo}", flush=True)

    random.seed(0)
    sim = Simulation(
        SimulationEngineCls=SAVSimulationEngine,
        percent_adoptions=(0.0, 0.1, 0.2, 0.5, 0.8, 0.99),
        scenario_configs=build_scenario_configs(**combo),
        output_dir=output_dir(**combo),
        num_trials=NUM_TRIALS,
        parse_cpus=int(os.environ.get("SLURM_NTASKS", 40)),
        ASGraphAnalyzerCls=SAVASGraphAnalyzer,
        GraphDataAggregatorCls=SAVMetricTracker,
    )
    sim.run()


if __name__ == "__main__":
    start = time()
    main()
    end = time()
    print(f"TOTAL RUNTIME: {end - start}")
