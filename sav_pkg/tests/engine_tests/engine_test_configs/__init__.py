from .config_000 import config_000
from .config_001 import config_001

from .loose_000 import loose_000

from .strict_000 import strict_000

engine_test_configs = [
    config_000,
    config_001,
    loose_000,
    strict_000,
]

__all__ = ["engine_test_configs"]