from .settings import Settings
from .config import Config,Rule

ENVIRONMENT = Settings.get_instance()
CONFIG = Config.get_instance()