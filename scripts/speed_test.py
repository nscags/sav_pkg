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
            # 0.1,
            # 0.2,
            # 0.5,
            # 0.8,
            # 0.99,
            # Using only 1 AS not adopting causes extreme variance
            # SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        scenario_configs=(
            SAVScenarioConfig(
                ScenarioCls=SAVScenarioExport2Some,
                scenario_label="speed_test",
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
    profiler.disable()
    s = io.StringIO()
    sortby = 'cumtime'
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    with Path('~/sav_speed_test.txt').expanduser().open('w+') as f:
        f.write(s.getvalue())