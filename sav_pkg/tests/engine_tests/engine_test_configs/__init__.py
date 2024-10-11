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
from .config_202 import config_202
from .config_203 import config_203
from .config_204 import config_204
from .config_205 import config_205
from .config_206 import config_206
from .config_207 import config_207
from .config_208 import config_208
from .config_209 import config_209
from .config_210 import config_210
from .config_211 import config_211
from .config_212 import config_212
from .config_213 import config_213

#config 2200- 2299: using graph 002
from .config_2200 import config_2200

#config 3200- 3299: using graph 003
from .config_3200 import config_3200

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
    # config_200,
    # config_201,
    # config_202,
    # config_203,
    # config_204,
    # config_205,
    # config_206,
    # config_207,
    # config_208,
    # config_209,
    # config_210,
    # config_211,
    # config_212,
    # config_213,
    # config_2200,
    config_3200,
    # config_300,
    # config_301,
    # config_302,
    # config_400,
    # config_401,
]

__all__ = ["engine_test_configs"]