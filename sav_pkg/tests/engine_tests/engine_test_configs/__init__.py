# EmptySAV
from .config_000 import config_000
from .config_001 import config_001
# Strict uRPF
from .config_100 import config_100
from .config_101 import config_101
# Feasible-Path uRPF
from .config_200 import config_200
from .config_201 import config_201
# EFP uRPF
from .config_300 import config_300
from .config_301 import config_301
# BAR SAV
from .config_400 import config_400
from .config_401 import config_401
from .config_402 import config_402
from .config_403 import config_403
from .config_404 import config_404
from .config_405 import config_405
from .config_406 import config_406


engine_test_configs = [
    config_000,
    config_001,
    config_100,
    config_101,
    config_200,
    config_201,
    # config_300,
    # config_301,
    # config_400,
    # config_401,
    # config_402,
    # config_403,
    # config_404,
    # config_405,
    # config_406,
]

__all__ = ["engine_test_configs"]
