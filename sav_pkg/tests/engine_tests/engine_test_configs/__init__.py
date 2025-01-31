from .ex_configs import ex_configs

from .strict_000 import strict_000

engine_test_configs = ex_configs + [
    strict_000,
]


__all__ = ["engine_test_configs"]