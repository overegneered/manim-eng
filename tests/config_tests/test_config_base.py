import copy
import dataclasses as dc
from typing import Any

import manim as mn
import pytest
from manim_eng._config.config import ConfigBase


@dc.dataclass
class TestConfigSubtable(ConfigBase):
    var_int: int = 4
    var_float: float = 3.14
    var_str: str = "a test string"
    var_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.RED)


@dc.dataclass
class TestConfigTable(ConfigBase):
    var_int: int = 4
    var_float: float = 3.14
    var_str: str = "a test string"
    var_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.RED)
    subtable: TestConfigSubtable = dc.field(
        default_factory=lambda: TestConfigSubtable()
    )


@dc.dataclass
class TestConfigRoot(ConfigBase):
    var_int: int = 4
    var_float: float = 3.14
    var_str: str = "a test string"
    var_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.RED)
    table: TestConfigTable = dc.field(default_factory=lambda: TestConfigTable())


@pytest.fixture()
def test_config() -> TestConfigRoot:
    return TestConfigRoot()


@pytest.mark.parametrize(
    ("dict_to_load", "match_pattern"),
    [
        pytest.param(
            {"not_present": 4},
            "Invalid key in manim-eng configuration: `not_present`",
            id="invalid key in root table",
        ),
        pytest.param(
            {"table": {"not_present": 4}},
            r"Invalid key in manim-eng configuration: `table\.not_present`",
            id="invalid key in top-level table",
        ),
        pytest.param(
            {"table": {"subtable": {"not_present": 4}}},
            r"Invalid key in manim-eng configuration: `table.subtable\.not_present`",
            id="invalid key in second-level table",
        ),
        pytest.param(
            {"invalid_table": {}},
            "Invalid table in manim-eng configuration: `invalid_table`",
            id="invalid table in root table",
        ),
        pytest.param(
            {"table": {"invalid_table": {}}},
            r"Invalid table in manim-eng configuration: `table\.invalid_table`",
            id="invalid table in first-level table",
        ),
        pytest.param(
            {"table": {"subtable": {"invalid_table": {}}}},
            r"Invalid table in manim-eng configuration: "
            r"`table\.subtable\.invalid_table`",
            id="invalid table in second-level table",
        ),
        pytest.param(
            {"var_int": {}},
            "Invalid table in manim-eng configuration: `var_int`",
            id="trying to set a table to a variable in the root table",
        ),
        pytest.param(
            {"table": {"var_int": {}}},
            r"Invalid table in manim-eng configuration: `table\.var_int`",
            id="trying to set a table to a variable in a first-level table",
        ),
        pytest.param(
            {"table": {"subtable": {"var_int": {}}}},
            r"Invalid table in manim-eng configuration: `table\.subtable\.var_int`",
            id="trying to set a table to a variable in a second-level table",
        ),
        pytest.param(
            {"var_int": 3.14},
            r"Invalid type in manim-eng configuration for key `var_int`: "
            r"float \(expected integer\)",
            id="trying to set a variable with the wrong type in the root table",
        ),
        pytest.param(
            {"table": {"var_int": 3.14}},
            r"Invalid type in manim-eng configuration for key `table\.var_int`: "
            r"float \(expected integer\)",
            id="trying to set a variable with the wrong type in a first-level table",
        ),
        pytest.param(
            {"table": {"subtable": {"var_int": 3.14}}},
            r"Invalid type in manim-eng configuration for key "
            r"`table\.subtable\.var_int`: float \(expected integer\)",
            id="trying to set a variable with the wrong type in a second-level table",
        ),
        pytest.param(
            {"var_colour": 3},
            r"Invalid type in manim-eng configuration for key `var_colour`: "
            r"integer \(expected string\)",
            id="trying to set a colour with the wrong type in the root table",
        ),
        pytest.param(
            {"table": {"var_colour": 3}},
            r"Invalid type in manim-eng configuration for key `table\.var_colour`: "
            r"integer \(expected string\)",
            id="trying to set a colour with the wrong type in a first-level table",
        ),
        pytest.param(
            {"table": {"subtable": {"var_colour": 3}}},
            r"Invalid type in manim-eng configuration for key "
            r"`table\.subtable\.var_colour`: integer \(expected string\)",
            id="trying to set a colour with the wrong type in a second-level table",
        ),
        pytest.param(
            {"var_colour": "jkfdsalfj"},
            "Invalid colour in manim-eng configuration for key `var_colour`: jkfdsalfj",
            id="invalid colour (keysmash)",
        ),
        pytest.param(
            {"var_colour": "#1DF34"},
            "Invalid colour in manim-eng configuration for key `var_colour`: #1DF34",
            id="invalid colour (not long enough)",
        ),
        pytest.param(
            {"var_colour": "#1DF34AA"},
            "Invalid colour in manim-eng configuration for key `var_colour`: #1DF34AA",
            id="invalid colour (too long)",
        ),
        pytest.param(
            {"var_colour": "1DF34A"},
            "Invalid colour in manim-eng configuration for key `var_colour`: 1DF34A",
            id="invalid colour (no hash)",
        ),
        pytest.param(
            {"var_colour": "#1SF34A"},
            "Invalid colour in manim-eng configuration for key `var_colour`: #1SF34A",
            id="invalid colour (invalid letters)",
        ),
    ],
)
def test_load_from_dict_with_invalid_config(
    dict_to_load: dict[str, Any], match_pattern: str, test_config: TestConfigRoot
) -> None:
    with pytest.raises(ValueError, match=match_pattern):
        test_config.load_from_dict(dict_to_load)


def test_load_from_dict_load_to_root_table(test_config: TestConfigRoot) -> None:
    test_config.load_from_dict({"var_str": "new value"})

    assert test_config.var_str == "new value"


def test_load_from_dict_load_to_first_level_table(test_config: TestConfigRoot) -> None:
    test_config.load_from_dict({"table": {"var_str": "new value"}})

    assert test_config.table.var_str == "new value"


def test_load_from_dict_load_to_second_level_table(test_config: TestConfigRoot) -> None:
    new_value = "new value"

    test_config.load_from_dict({"table": {"subtable": {"var_str": "new value"}}})

    assert test_config.table.subtable.var_str == new_value


def test_load_from_dict_load_multiple(test_config: TestConfigRoot) -> None:
    config_dict = {
        "var_int": 987654321,
        "var_float": 2.718,
        "table": {
            "var_str": "new value",
            "subtable": {
                "var_int": 123456789,
            },
        },
    }

    test_config.load_from_dict(config_dict)

    assert test_config.var_int == 987654321  # noqa: PLR2004
    assert test_config.var_float == 2.718  # noqa: PLR2004
    assert test_config.table.var_str == "new value"
    assert test_config.table.subtable.var_int == 123456789  # noqa: PLR2004


def test_load_from_dict_load_empty_dict_does_nothing(
    test_config: TestConfigRoot,
) -> None:
    original_config = copy.deepcopy(test_config)

    test_config.load_from_dict({})

    assert test_config == original_config


@pytest.mark.parametrize(
    ("colour_string", "colour_manim"),
    [
        pytest.param("white", mn.WHITE, id="white"),
        pytest.param("gray_a", mn.GRAY_A, id="gray_a"),
        pytest.param("grey_a", mn.GREY_A, id="grey_a"),
        pytest.param("gray_b", mn.GRAY_B, id="gray_b"),
        pytest.param("grey_b", mn.GREY_B, id="grey_b"),
        pytest.param("gray_c", mn.GRAY_C, id="gray_c"),
        pytest.param("grey_c", mn.GREY_C, id="grey_c"),
        pytest.param("gray_d", mn.GRAY_D, id="gray_d"),
        pytest.param("grey_d", mn.GREY_D, id="grey_d"),
        pytest.param("gray_e", mn.GRAY_E, id="gray_e"),
        pytest.param("grey_e", mn.GREY_E, id="grey_e"),
        pytest.param("black", mn.BLACK, id="black"),
        pytest.param("lighter_gray", mn.LIGHTER_GRAY, id="lighter_gray"),
        pytest.param("lighter_grey", mn.LIGHTER_GREY, id="lighter_grey"),
        pytest.param("light_gray", mn.LIGHT_GRAY, id="light_gray"),
        pytest.param("light_grey", mn.LIGHT_GREY, id="light_grey"),
        pytest.param("gray", mn.GRAY, id="gray"),
        pytest.param("grey", mn.GREY, id="grey"),
        pytest.param("dark_gray", mn.DARK_GRAY, id="dark_gray"),
        pytest.param("dark_grey", mn.DARK_GREY, id="dark_grey"),
        pytest.param("darker_gray", mn.DARKER_GRAY, id="darker_gray"),
        pytest.param("darker_grey", mn.DARKER_GREY, id="darker_grey"),
        pytest.param("blue_a", mn.BLUE_A, id="blue_a"),
        pytest.param("blue_b", mn.BLUE_B, id="blue_b"),
        pytest.param("blue_c", mn.BLUE_C, id="blue_c"),
        pytest.param("blue_d", mn.BLUE_D, id="blue_d"),
        pytest.param("blue_e", mn.BLUE_E, id="blue_e"),
        pytest.param("pure_blue", mn.PURE_BLUE, id="pure_blue"),
        pytest.param("blue", mn.BLUE, id="blue"),
        pytest.param("dark_blue", mn.DARK_BLUE, id="dark_blue"),
        pytest.param("teal_a", mn.TEAL_A, id="teal_a"),
        pytest.param("teal_b", mn.TEAL_B, id="teal_b"),
        pytest.param("teal_c", mn.TEAL_C, id="teal_c"),
        pytest.param("teal_d", mn.TEAL_D, id="teal_d"),
        pytest.param("teal_e", mn.TEAL_E, id="teal_e"),
        pytest.param("teal", mn.TEAL, id="teal"),
        pytest.param("green_a", mn.GREEN_A, id="green_a"),
        pytest.param("green_b", mn.GREEN_B, id="green_b"),
        pytest.param("green_c", mn.GREEN_C, id="green_c"),
        pytest.param("green_d", mn.GREEN_D, id="green_d"),
        pytest.param("green_e", mn.GREEN_E, id="green_e"),
        pytest.param("pure_green", mn.PURE_GREEN, id="pure_green"),
        pytest.param("green", mn.GREEN, id="green"),
        pytest.param("yellow_a", mn.YELLOW_A, id="yellow_a"),
        pytest.param("yellow_b", mn.YELLOW_B, id="yellow_b"),
        pytest.param("yellow_c", mn.YELLOW_C, id="yellow_c"),
        pytest.param("yellow_d", mn.YELLOW_D, id="yellow_d"),
        pytest.param("yellow_e", mn.YELLOW_E, id="yellow_e"),
        pytest.param("yellow", mn.YELLOW, id="yellow"),
        pytest.param("gold_a", mn.GOLD_A, id="gold_a"),
        pytest.param("gold_b", mn.GOLD_B, id="gold_b"),
        pytest.param("gold_c", mn.GOLD_C, id="gold_c"),
        pytest.param("gold_d", mn.GOLD_D, id="gold_d"),
        pytest.param("gold_e", mn.GOLD_E, id="gold_e"),
        pytest.param("gold", mn.GOLD, id="gold"),
        pytest.param("red_a", mn.RED_A, id="red_a"),
        pytest.param("red_b", mn.RED_B, id="red_b"),
        pytest.param("red_c", mn.RED_C, id="red_c"),
        pytest.param("red_d", mn.RED_D, id="red_d"),
        pytest.param("red_e", mn.RED_E, id="red_e"),
        pytest.param("pure_red", mn.PURE_RED, id="pure_red"),
        pytest.param("red", mn.RED, id="red"),
        pytest.param("maroon_a", mn.MAROON_A, id="maroon_a"),
        pytest.param("maroon_b", mn.MAROON_B, id="maroon_b"),
        pytest.param("maroon_c", mn.MAROON_C, id="maroon_c"),
        pytest.param("maroon_d", mn.MAROON_D, id="maroon_d"),
        pytest.param("maroon_e", mn.MAROON_E, id="maroon_e"),
        pytest.param("maroon", mn.MAROON, id="maroon"),
        pytest.param("purple_a", mn.PURPLE_A, id="purple_a"),
        pytest.param("purple_b", mn.PURPLE_B, id="purple_b"),
        pytest.param("purple_c", mn.PURPLE_C, id="purple_c"),
        pytest.param("purple_d", mn.PURPLE_D, id="purple_d"),
        pytest.param("purple_e", mn.PURPLE_E, id="purple_e"),
        pytest.param("purple", mn.PURPLE, id="purple"),
        pytest.param("pink", mn.PINK, id="pink"),
        pytest.param("light_pink", mn.LIGHT_PINK, id="light_pink"),
        pytest.param("orange", mn.ORANGE, id="orange"),
        pytest.param("light_brown", mn.LIGHT_BROWN, id="light_brown"),
        pytest.param("dark_brown", mn.DARK_BROWN, id="dark_brown"),
        pytest.param("gray_brown", mn.GRAY_BROWN, id="gray_brown"),
        pytest.param("grey_brown", mn.GREY_BROWN, id="grey_brown"),
        pytest.param("logo_white", mn.LOGO_WHITE, id="logo_white"),
        pytest.param("logo_green", mn.LOGO_GREEN, id="logo_green"),
        pytest.param("logo_blue", mn.LOGO_BLUE, id="logo_blue"),
        pytest.param("logo_red", mn.LOGO_RED, id="logo_red"),
        pytest.param("logo_black", mn.LOGO_BLACK, id="logo_black"),
        pytest.param("#123456", mn.ManimColor("#123456"), id="hex code 1"),
        pytest.param("#ABCDEF", mn.ManimColor("#ABCDEF"), id="hex code 2"),
        pytest.param("#123abC", mn.ManimColor("#123ABC"), id="hex code 3"),
    ],
)
def test_load_from_dict_with_string_representation_of_colour(
    test_config: TestConfigRoot, colour_string: str, colour_manim: mn.ManimColor
) -> None:
    config_dict = {
        "var_colour": colour_string,
    }

    test_config.load_from_dict(config_dict)

    assert test_config.var_colour == colour_manim


def test_load_from_dict_with_manim_representation_of_colour(
    test_config: TestConfigRoot,
) -> None:
    config_dict = {
        "var_colour": mn.PURPLE_C,
    }

    test_config.load_from_dict(config_dict)

    assert test_config.var_colour == mn.PURPLE_C


def test_as_dict(test_config: TestConfigRoot) -> None:
    expected = {
        "var_int": 4,
        "var_float": 3.14,
        "var_str": "a test string",
        "var_colour": mn.RED,
        "table": {
            "var_int": 4,
            "var_float": 3.14,
            "var_str": "a test string",
            "var_colour": mn.RED,
            "subtable": {
                "var_int": 4,
                "var_float": 3.14,
                "var_str": "a test string",
                "var_colour": mn.RED,
            },
        },
    }

    actual = test_config.as_dict()

    assert actual == expected


@pytest.mark.parametrize(
    ("variable", "expected"),
    [
        pytest.param("", "string", id="string"),
        pytest.param(1, "integer", id="integer"),
        pytest.param(3.14, "float", id="float"),
        pytest.param(True, "boolean", id="boolean"),
        pytest.param([], "array", id="array"),
        pytest.param({}, "table", id="table"),
        pytest.param(mn.BLUE, "string", id="colours should be stored as strings"),
        pytest.param(
            ConfigBase(), "table", id="other custom Python types should be tables"
        ),
    ],
)
def test_get_toml_type_from_pyton_variable(variable: Any, expected: str) -> None:
    assert ConfigBase._get_toml_type_from_python_variable(variable) == expected
