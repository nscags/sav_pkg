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
from .config_012 import config_012
from .config_013 import config_013
from .config_014 import config_014
from .config_015 import config_015
from .config_016 import config_016

engine_test_configs = [
    # config_000,
    # config_001,
    # config_002,
    # config_003,
    # config_004,
    # config_005,
    # # config_006, # Both 006-007 have some manual configuations
    # # config_007, # Don't rerun or graphs will be wrong
    # config_008,
    # config_009,
    config_010,
    config_011,
    config_012,
    config_013,
    config_014,
    config_015,
    # config_016, # Don't run
]

__all__ = ["engine_test_configs"]
