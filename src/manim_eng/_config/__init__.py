import contextlib
import copy
from typing import Any, Generator

from .config import ManimEngConfig
from .config_readers import get_project_config, get_user_config

__all__ = ["config_eng", "tempconfig_eng"]


config_eng = (
    ManimEngConfig()
    .load_from_dict(get_user_config())
    .load_from_dict(get_project_config())
)


@contextlib.contextmanager
def tempconfig_eng(temp_config: dict[str, Any]) -> Generator:
    global config_eng  # noqa: PLW0602
    original = copy.deepcopy(config_eng).as_dict()

    config_eng.load_from_dict(temp_config)

    try:
        yield
    finally:
        # Note that we load here instead of assigning so that we update the original
        # object.
        config_eng.load_from_dict(original)
