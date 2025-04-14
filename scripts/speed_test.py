import cProfile
import io
import pstats
import time
from pathlib import Path

from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_engine import BGP
from bgpy.simulation_framework import (
    Simulation,
)

from sav_pkg.simulation_framework.scenarios import (
    SAVScenarioConfig,
    SAVScenarioExport2Some,
)
from sav_pkg.policies import LooseuRPF, BGPExport2Some
from sav_pkg.utils.utils import get_export_to_some_dict


def main():
    """Runs the defaults"""

    # Simulation for the paper
    bgp_e2s_asn_cls_dict = get_export_to_some_dict(e2s_policy=BGPExport2Some)
    sim = Simulation(
        percent_adoptions=(
            SpecialPercentAdoptions.ONLY_ONE,
            0.1,
            0.2,
            0.5,
            0.8,
            0.99,
            # Using only 1 AS not adopting causes extreme variance
            # SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        scenario_configs=(
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioExport2Some,
                BaseSAVPolicyCls=LooseuRPF,
                reflector_default_adopters=True,
                scenario_label="loose",
                hardcoded_asn_cls_dict=bgp_e2s_asn_cls_dict
            ),
        ),
        output_dir=Path("~/sav/results/speed_test").expanduser(),
        num_trials=1,
        parse_cpus=1,
    )
    sim.run(GraphFactoryCls=None)


if __name__ == "__main__":
    start = time.perf_counter()
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    print(f"{time.perf_counter() - start:.2f}s")
    # v9 Normal 61.6s
    # v8 68.53s
    # v9 again only 63.88s
    # CIBUILDWHEEL=1 pip install frozendict - 64s
    # After removing 5% info tag from announcements
    profiler.disable()

    # Create a StringIO object to capture the profiling results
    s = io.StringIO()

    # Create a Stats object with the profiling results
    sortby = 'cumtime'
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)

    # Print the profiling results to the StringIO object
    ps.print_stats()

    # Write the profiling results to a file
    with open('~/sav/results/speed_test/speed_test.txt', 'w') as f:
        f.write(s.getvalue())