from functools import lru_cache
from .settings import Settings

ENVIRONMENT = Settings.get_instance()