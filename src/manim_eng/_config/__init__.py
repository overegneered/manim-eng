from .config import ManimEngConfig
from .config_readers import get_project_config, get_user_config

config_eng = (
    ManimEngConfig()
    .load_from_dict(get_user_config())
    .load_from_dict(get_project_config())
)

__all__ = ["config_eng"]
