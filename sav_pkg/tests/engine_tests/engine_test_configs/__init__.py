from .config_000 import config_000
from .config_001 import config_001
from .config_002 import config_002
from .config_003 import config_003
from .config_004 import config_004
from .config_005 import config_005

from .loose_000 import loose_000

from .strict_000 import strict_000

engine_test_configs = [
    config_000,
    config_001,
    config_002,
    config_003,
    config_004,
    # config_005,
    loose_000,
    strict_000,
]

__all__ = ["engine_test_configs"]