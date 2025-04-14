# General System Tests
from .config_000 import config_000
from .config_001 import config_001
from .config_002 import config_002
from .config_003 import config_003
from .config_004 import config_004
from .config_005 import config_005
from .config_006 import config_006
from .config_007 import config_007
from .config_008 import config_008
from .config_009 import config_009
from .config_010 import config_010
from .config_011 import config_011

# SAV Policy Tests
from .loose_000 import loose_000
from .strict_000 import strict_000
from .fp_000 import fp_000
from .efp_alg_a_000 import efp_alg_a_000
from .efp_alg_a_wo_peers_000 import efp_alg_a_wo_peers_000
from .efp_alg_b_000 import efp_alg_b_000
from .rfc8704_000 import rfc8704_000
from .refined_alg_a_000 import refined_alg_a_000
from .refined_alg_a_001 import refined_alg_a_001
from .refined_alg_a_002 import refined_alg_a_002


engine_test_configs = [
    # config_000,
    # config_001,
    # config_002,
    # config_003,
    # config_004,
    # config_005,
    # config_006,
    # config_007,
    # config_008,
    # config_009,
    # config_010,
    config_011,
    # loose_000,
    # strict_000,
    # fp_000,
    # efp_alg_a_000,
    # efp_alg_a_wo_peers_000,
    # efp_alg_b_000,
    # rfc8704_000,
    # refined_alg_a_000,
    # refined_alg_a_001,
    # refined_alg_a_002,
]

__all__ = ["engine_test_configs"]