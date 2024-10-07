# Initial Tests 
# from .config_001 import config_001
# from .config_002 import config_002
# from .config_003 import config_003
# from .config_004 import config_004

# Strict uRPF (config_100 - config_199)
from .config_100 import config_100
from .config_101 import config_101

# Feasible-Path uRPF (config_200 - config_299)
from .config_200 import config_200
from .config_201 import config_201

# EFP uRPF (config_300 - config_399)
from .config_300 import config_300
from .config_301 import config_301
from .config_302 import config_302

# BAR SAV (config_400 - config_499)
from .config_400 import config_400
from .config_401 import config_401


engine_test_configs = [
    # config_001,
    # config_002,
    # config_003,
    # config_004,
    # config_100,
    # config_101,
    config_200,
    config_201,
    config_300,
    config_301,
    # config_302,
    config_400,
    config_401,
]

__all__ = ["engine_test_configs"]