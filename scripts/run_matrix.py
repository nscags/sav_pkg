import argparse
import os
import random
from time import time

from bgpy.simulation_framework import Simulation

from sav_pkg.simulation_engine.background_routes import RouteStore
from sav_pkg.simulation_engine.sav_simulation_engine import SAVSimulationEngine
from sav_pkg.simulation_framework.sav_as_graph_analyzer import SAVASGraphAnalyzer
from sav_pkg.simulation_framework.metric_tracker.metric_tracker import SAVMetricTracker

from matrix import (
    MATRIX,
    NUM_TRIALS,
    as_graph_constructor_kwargs,
    build_scenario_configs,
    claim_output_dir,
    output_dir,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index", type=int, default=None,
        help="MATRIX index (default: SLURM_ARRAY_TASK_ID)",
    )
    parser.add_argument(
        "--trials", type=int, default=NUM_TRIALS,
        help=f"Number of trials (default {NUM_TRIALS}); shows up in the output dir name",
    )
    args, _unknown = parser.parse_known_args()
    if args.index is None:
        if "SLURM_ARRAY_TASK_ID" not in os.environ:
            parser.error("--index is required outside a SLURM array job")
        args.index = int(os.environ["SLURM_ARRAY_TASK_ID"])
    return args


def main():
    args = parse_args()
    index, num_trials = args.index, args.trials
    combo = MATRIX[index]
    out_dir = claim_output_dir(output_dir(**combo, num_trials=num_trials))
    print(f"Running matrix index {index}: {combo}", flush=True)
    print(f"Writing results to {out_dir}", flush=True)

    scenario_configs = build_scenario_configs(**combo)
    # *_wp scenarios: open the background routes now, so a missing nh.npy
    # fails here instead of inside a worker
    for routes_dir in {c.routes_dir for c in scenario_configs if c.routes_dir}:
        print(f"Background routes: {RouteStore.get(routes_dir).nh.shape} from {routes_dir}",
              flush=True)

    random.seed(0)
    sim = Simulation(
        SimulationEngineCls=SAVSimulationEngine,
        percent_adoptions=(0.0, 0.1, 0.2, 0.5, 0.8, 0.99),
        scenario_configs=scenario_configs,
        output_dir=out_dir,
        num_trials=num_trials,
        parse_cpus=int(os.environ.get("SLURM_NTASKS", 40)),
        ASGraphAnalyzerCls=SAVASGraphAnalyzer,
        GraphDataAggregatorCls=SAVMetricTracker,
        as_graph_constructor_kwargs=as_graph_constructor_kwargs(),
    )
    sim.run()


if __name__ == "__main__":
    start = time()
    main()
    end = time()
    print(f"TOTAL RUNTIME: {end - start}")
