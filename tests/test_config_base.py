import copy
import dataclasses as dc
from typing import Any

import pytest
from manim_eng._config.config import ConfigBase


@dc.dataclass
class SubTable(ConfigBase):
    var_int: int = 4
    var_float: float = 3.14
    var_str: str = "a test string"


@dc.dataclass
class Table(ConfigBase):
    var_int: int = 4
    var_float: float = 3.14
    var_str: str = "a test string"
    subtable: SubTable = dc.field(default_factory=lambda: SubTable())


@dc.dataclass
class Root(ConfigBase):
    var_int: int = 4
    var_float: float = 3.14
    var_str: str = "a test string"
    table: Table = dc.field(default_factory=lambda: Table())


@pytest.fixture()
def test_config() -> Root:
    return Root()


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
    ],
)
def test_load_from_dict_with_invalid_config(
    dict_to_load: dict[str, Any], match_pattern: str, test_config: Root
) -> None:
    with pytest.raises(ValueError, match=match_pattern):
        test_config.load_from_dict(dict_to_load)


def test_load_from_dict_load_to_root_table(test_config: Root) -> None:
    test_config.load_from_dict({"var_str": "new value"})

    assert test_config.var_str == "new value"


def test_load_from_dict_load_to_first_level_table(test_config: Root) -> None:
    test_config.load_from_dict({"table": {"var_str": "new value"}})

    assert test_config.table.var_str == "new value"


def test_load_from_dict_load_to_second_level_table(test_config: Root) -> None:
    new_value = "new value"

    test_config.load_from_dict({"table": {"subtable": {"var_str": "new value"}}})

    assert test_config.table.subtable.var_str == new_value


def test_load_from_dict_load_multiple(test_config: Root) -> None:
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


def test_load_from_dict_load_empty_dict_does_nothing(test_config: Root) -> None:
    original_config = copy.deepcopy(test_config)

    test_config.load_from_dict({})

    assert test_config == original_config


@pytest.mark.parametrize(
    ("variable", "expected"),
    [
        pytest.param("", "string", id="string"),
        pytest.param(1, "integer", id="integer"),
        pytest.param(3.14, "float", id="float"),
        pytest.param(True, "boolean", id="boolean"),
        pytest.param([], "array", id="array"),
        pytest.param({}, "table", id="table"),
        pytest.param(ConfigBase(), "table", id="custom Python type should be table"),
    ],
)
def test_get_toml_type_from_pyton_variable(variable: Any, expected: str) -> None:
    assert ConfigBase.get_toml_type_from_python_variable(variable) == expected
