from .config_dsr_000 import config_dsr_000
from .config_dsr_001 import config_dsr_001
from .config_dsr_002 import config_dsr_002
from .config_dsr_003 import config_dsr_003


engine_test_configs = [
    config_dsr_000,
    config_dsr_001,
    config_dsr_002,
    config_dsr_003,
]

__all__ = ["engine_test_configs"]