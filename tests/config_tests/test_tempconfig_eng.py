import copy

from manim_eng._config import config_eng, tempconfig_eng


def test_tempconfig_eng() -> None:
    original = copy.deepcopy(config_eng)

    with tempconfig_eng({"debug": True, "symbol": {"bipole_height": 1000.0}}):
        assert config_eng.debug is True
        assert config_eng.symbol.bipole_height == 1000.0  # noqa: PLR2004

    assert config_eng == original
