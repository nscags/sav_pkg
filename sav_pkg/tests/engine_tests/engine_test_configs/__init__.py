from .ex_configs import ex_configs

from .e2s_ps_000 import e2s_ps_000

from .loose_000 import loose_000

from .strict_000 import strict_000
from .strict_001 import strict_001
from .strict_002 import strict_002
from .strict_003 import strict_003
from .strict_004 import strict_004
from .strict_005 import strict_005
from .strict_006 import strict_006
from .strict_007 import strict_007

from .fp_000 import fp_000
from .fp_001 import fp_001
from .fp_002 import fp_002
from .fp_003 import fp_003
from .fp_004 import fp_004

from .efp_b_000 import efp_b_000
from .efp_b_001 import efp_b_001
from .efp_b_002 import efp_b_002

from .efp_a_000 import efp_a_000
from .efp_a_001 import efp_a_001
from .efp_a_002 import efp_a_002
from .efp_a_003 import efp_a_003

from .efp_a_w_peers_000 import efp_a_w_peers_000

from .bar_sav_000 import bar_sav_000 
from .bar_sav_001 import bar_sav_001
from .bar_sav_002 import bar_sav_002
from .bar_sav_003 import bar_sav_003
from .bar_sav_004 import bar_sav_004
from .bar_sav_005 import bar_sav_005
from .bar_sav_006 import bar_sav_006
from .bar_sav_007 import bar_sav_007
from .bar_sav_008 import bar_sav_008
from .bar_sav_009 import bar_sav_009


engine_test_configs = [
    e2s_ps_000,
    # loose_000,
    # strict_000,
    # strict_001,
    # strict_002,
    # strict_003,
    # strict_004,
    # strict_005,
    # strict_006,
    # strict_007,
    # fp_000,
    # fp_001,
    # fp_002,
    # fp_003,
    # fp_004, # don't run, needs manual config
    # efp_b_000,
    # efp_b_001,
    # efp_b_002,
    # efp_a_000,
    # efp_a_001,
    # efp_a_002,
    # efp_a_003,
    # efp_a_w_peers_000,
    # bar_sav_000,
    # bar_sav_001,
    # bar_sav_002,
    # bar_sav_003,
    # bar_sav_004,
    # bar_sav_005,
    # bar_sav_006,
    # bar_sav_007,
    # bar_sav_008,
    # bar_sav_009,
] # + ex_configs

__all__ = ["engine_test_configs"]