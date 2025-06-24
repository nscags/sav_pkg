from .loose import loose_test_configs
from .strict import strict_test_configs
from .feasible import feasible_test_configs
from .efp_alg_a import efp_alg_a_test_configs
from .efp_alg_b import efp_alg_b_test_configs
from .refined_alg_a import refined_alg_a_test_configs


engine_test_configs = (
    loose_test_configs +
    strict_test_configs +
    feasible_test_configs +
    efp_alg_a_test_configs +
    efp_alg_b_test_configs +
    refined_alg_a_test_configs
)

__all__ = ["engine_test_configs"]