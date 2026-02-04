from .strict import strict_test_configs
from .fp import fp_test_configs
from .efp_a import efp_a_test_configs
from .efp_a_w_peers import efp_a_w_peers_test_configs
from .efp_b import efp_b_test_configs
from .bar_sav import bar_sav_test_configs


engine_test_configs = (
    strict_test_configs +
    fp_test_configs +
    efp_a_test_configs +
    efp_a_w_peers_test_configs +
    efp_b_test_configs +
    bar_sav_test_configs
)

__all__ = ["engine_test_configs"]