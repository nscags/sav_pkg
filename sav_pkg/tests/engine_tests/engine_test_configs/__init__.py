# Initial Tests 
# from .config_001 import config_001
# from .config_002 import config_002
# from .config_003 import config_003
# from .config_004 import config_004
from .config_005 import config_005
from .config_006 import config_006

# Strict uRPF (config_100 - config_199)
from .config_100 import config_100
from .config_101 import config_101

from .config_102 import config_102
from .config_103 import config_103
from .config_104 import config_104
from .config_105 import config_105
from .config_106 import config_106
from .config_107 import config_107
from .config_108 import config_108
from .config_109 import config_109
from .config_110 import config_110
from .config_111 import config_111
from .config_112 import config_112
from .config_113 import config_113
from .config_114 import config_114

#config 2200- 2299: using graph 002

# from .config_2100 import config_2100

#config 3200- 3299: using graph 003
from .config_3100 import config_3100
from .config_3101 import config_3101
from .config_3102 import config_3102
from .config_3103 import config_3103
from .config_3104 import config_3104
from .config_3105 import config_3105
from .config_3106 import config_3106
from .config_3107 import config_3107


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
from .config_214 import config_214

#config 2200- 2299: using graph 002
from .config_2200 import config_2200

#config 3200- 3299: using graph 003
from .config_3200 import config_3200
from .config_3201 import config_3201
from .config_3202 import config_3202
from .config_3203 import config_3203
from .config_3204 import config_3204
from .config_3205 import config_3205
from .config_3206 import config_3206
from .config_3207 import config_3207



# EFP uRPF (config_300 - config_399)
from .config_300 import config_300
from .config_301 import config_301
# from .config_302 import config_302 # Do not run this one, doesn't work

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
    # config_214,
    # config_3201,
    # config_3202,
    # config_3203,
    # config_3204,
    # config_3205,
    # config_3206,
    # config_3207,

    config_101,
    config_102,
    config_103,
    config_104,
    config_105,
    config_106,
    config_107,
    config_108,
    config_109,
    config_110,
    config_111,
    config_112,
    config_113,
    config_114,

    config_3100,
    config_3101,
    config_3102,
    config_3103,
    config_3104,
    config_3105,
    config_3106,
    config_3107,


    # config_2200,

    # config_300,
    # config_301,
    # config_302,
    # config_400,
    # config_401,
]

__all__ = ["engine_test_configs"]