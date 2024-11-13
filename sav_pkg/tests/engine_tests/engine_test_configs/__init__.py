# Loose uRPF (config_000 - config_099)


# Strict uRPF (config_100 - config_199) <-
from .config_100 import config_100
from .config_101 import config_101
from .config_102 import config_102
from .config_103 import config_103
from .config_104 import config_104
from .config_105 import config_105

# Feasible-Path uRPF (config_200 - config_299) <-
from .config_200 import config_200
from .config_201 import config_201
from .config_202 import config_202

# EFP uRPF (config_300 - config_399) <-
from .config_300 import config_300
from .config_301 import config_301
from .config_302 import config_302
from .config_303 import config_303
from .config_304 import config_304
from .config_305 import config_305
from .config_306 import config_306

# BAR SAV (config_400 - config_499) <- 


# Feasible Path uRPF No Peers (config_500 - config_599) 


# RFC 8704 (config_600 - config_699)


# EFP uRPF Algorithm A (config_700 - config_799)


engine_test_configs = [
    config_100,
    config_101,
    config_102,
    config_103,
    config_104,
    config_105,
    config_200,
    config_201,
    config_202,
    config_300,
    config_301,
    config_302,
    config_303,
    config_304,
    config_305,
    config_306,
]

__all__ = ["engine_test_configs"]