# General System Tests
from .config_000 import config_000
from .config_001 import config_001
# from .config_002 import config_002
from .config_003 import config_003
from .config_004 import config_004
from .config_005 import config_005
from .config_006 import config_006
from .config_007 import config_007
from .config_008 import config_008
from .config_009 import config_009
from .config_010 import config_010
from .config_011 import config_011
from .config_012 import config_012
from .config_013 import config_013
from .config_014 import config_014

from .config_dsr_000 import config_dsr_000
from .config_dsr_001 import config_dsr_001
from .config_dsr_002 import config_dsr_002
from .config_dsr_003 import config_dsr_003
from .config_dsr_004 import config_dsr_004

from .test_000 import test_000

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
from .bar_sav_pi_000 import bar_sav_pi_000


engine_test_configs = [
    # test_000,
    # config_dsr_000,
    # config_dsr_001,
    # config_dsr_002,
    # config_dsr_003,
    # config_dsr_004,
    # config_000,
    # config_001,
    # config_003,
    # config_004,
    # config_005,
    # config_006,
    # config_007,
    # config_008,
    # config_009,
    # config_010,
    # config_011,
    # config_012,
    # config_013,
    # config_014,
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
    bar_sav_pi_000,
]

__all__ = ["engine_test_configs"]
