from typing import Any

import manim as mn
import pytest
from manim_eng._base.component import Component
from manim_eng._base.terminal import Terminal


class DummyComponent(Component):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        terminal = Terminal(mn.RIGHT, mn.RIGHT)
        other_terminal = Terminal(mn.LEFT, mn.LEFT)
        self.not_a_terminal = 3
        super().__init__([terminal, other_terminal], *args, **kwargs)

    def _construct(self) -> None:
        pass

    @property
    def terminal(self) -> Terminal:
        return self._terminals[0]

    @property
    def other_terminal(self) -> Terminal:
        return self._terminals[1]


@pytest.fixture()
def dummy_component() -> Component:
    return DummyComponent()


def test_set_label_no_existing_label(dummy_component: Component) -> None:
    label = "R"

    dummy_component.set_label(label)

    assert dummy_component._label.tex_strings == [label]


def test_set_label_existing_label(dummy_component: Component) -> None:
    dummy_component.set_label("old")
    new_label_text = "new"

    dummy_component.set_label(new_label_text)

    assert dummy_component._label.tex_strings == [new_label_text]


def test_set_annotation_no_existing_annotation(dummy_component: Component) -> None:
    annotation = r"12 \Omega"

    dummy_component.set_annotation(annotation)

    assert dummy_component._annotation.tex_strings == [annotation]


def test_set_annotation_existing_annotation(dummy_component: Component) -> None:
    dummy_component.set_annotation("old")
    new_annotation_text = "new"

    dummy_component.set_annotation(new_annotation_text)

    assert dummy_component._annotation.tex_strings == [new_annotation_text]


def test_label_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(label="R")

    assert dummy_component._label.tex_strings == ["R"]


def test_annotation_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(annotation=r"12 \Omega")

    assert dummy_component._annotation.tex_strings == [r"12 \Omega"]


def test_label_and_annotation_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(label="Z", annotation=r"(2 + j4) \,\Omega")

    assert dummy_component._label.tex_strings == ["Z"]
    assert dummy_component._annotation.tex_strings == [r"(2 + j4) \,\Omega"]


def test_voltage_processes_terminals_correctly(dummy_component: DummyComponent) -> None:
    voltage_1 = dummy_component.voltage(
        dummy_component.terminal,
        dummy_component.other_terminal,
        "V",
    )
    voltage_2 = dummy_component.voltage("terminal", dummy_component.other_terminal, "V")
    voltage_3 = dummy_component.voltage(dummy_component.terminal, "other_terminal", "V")
    voltage_4 = dummy_component.voltage("terminal", "other_terminal", "V")

    assert voltage_1.from_terminal == dummy_component.terminal
    assert voltage_1.to_terminal == dummy_component.other_terminal
    assert voltage_2.from_terminal == dummy_component.terminal
    assert voltage_2.to_terminal == dummy_component.other_terminal
    assert voltage_3.from_terminal == dummy_component.terminal
    assert voltage_3.to_terminal == dummy_component.other_terminal
    assert voltage_4.from_terminal == dummy_component.terminal
    assert voltage_4.to_terminal == dummy_component.other_terminal


def test_voltage_sets_component_it_is_called_on_as_avoid(
    dummy_component: DummyComponent,
) -> None:
    voltage = dummy_component.voltage("terminal", "other_terminal", "V")

    assert voltage.component_to_avoid == dummy_component


def test_voltage_errors_if_terminals_are_the_same(
    dummy_component: DummyComponent,
) -> None:
    expected_message = (
        "The terminals specified through `from_terminal` and "
        "`to_terminal` are identical."
    )

    with pytest.raises(ValueError, match=expected_message):
        dummy_component.voltage(dummy_component.terminal, dummy_component.terminal)
    with pytest.raises(ValueError, match=expected_message):
        dummy_component.voltage("terminal", dummy_component.terminal)
    with pytest.raises(ValueError, match=expected_message):
        dummy_component.voltage(dummy_component.terminal, "terminal")
    with pytest.raises(ValueError, match=expected_message):
        dummy_component.voltage("terminal", "terminal")


def test_get_or_check_terminal_non_belonging_terminal() -> None:
    component = DummyComponent()
    other_component = DummyComponent()

    with pytest.raises(
        ValueError, match="Passed terminal does not belong to this component."
    ):
        component._get_or_check_terminal(other_component.terminal)


def test_get_or_check_terminal_invalid_attribute(
    dummy_component: DummyComponent,
) -> None:
    with pytest.raises(AttributeError):
        dummy_component._get_or_check_terminal("invalid_attribute")


def test_get_or_check_terminal_valid_attribute_not_a_terminal(
    dummy_component: DummyComponent,
) -> None:
    not_a_terminal = "not_a_terminal"

    with pytest.raises(
        ValueError,
        match=f"Attribute `{not_a_terminal}` of `DummyComponent` is not a terminal.",
    ):
        dummy_component._get_or_check_terminal(not_a_terminal)


def test_get_or_check_terminal_valid_terminal(dummy_component: DummyComponent) -> None:
    result = dummy_component._get_or_check_terminal(dummy_component.terminal)

    assert result == dummy_component.terminal


def test_get_or_check_terminal_valid_string(dummy_component: DummyComponent) -> None:
    result = dummy_component._get_or_check_terminal("terminal")

    assert result == dummy_component.terminal
