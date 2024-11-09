# Strict uRPF (config_100 - config_199)
from .config_100 import config_100
from .config_101 import config_101
from .config_102 import config_102
from .config_103 import config_103
from .config_104 import config_104

# Feasible-Path uRPF (config_200 - config_299)
from .config_200 import config_200
from .config_201 import config_201
from .config_202 import config_202
from .config_203 import config_203
from .config_204 import config_204

# EFP uRPF (config_300 - config_399)
from .config_300 import config_300
from .config_301 import config_301
from .config_302 import config_302
from .config_303 import config_303

# BAR SAV (config_400 - config_499)
from .config_400 import config_400
from .config_401 import config_401

# Feasible Path uRPF No Peers (config_500 - config_599) 
from .config_500 import config_500
from .config_501 import config_501

engine_test_configs = [
    config_100,
    config_101,
    config_102,
    config_103,
    config_104,
    # config_204,
    # config_500,
    # config_501,
]

__all__ = ["engine_test_configs"]