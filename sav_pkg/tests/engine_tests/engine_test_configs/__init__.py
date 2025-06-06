from .config_005 import config_005

from .config_dsr_000 import config_dsr_000
from .config_dsr_001 import config_dsr_001
from .config_dsr_002 import config_dsr_002
from .config_dsr_003 import config_dsr_003
from .config_dsr_004 import config_dsr_004
from .config_dsr_005 import config_dsr_005


engine_test_configs = [
    config_005,
    config_dsr_000,
    config_dsr_001,
    config_dsr_002,
    config_dsr_003,
    config_dsr_004,
    config_dsr_005,
]

__all__ = ["engine_test_configs"]