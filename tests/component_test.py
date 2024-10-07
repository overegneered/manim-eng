import pytest
from manim_eng.components.base.component import Component

from .test_utils.dummy_component import DummyComponent, DummyComponentMockedTerminals


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
        dummy_component.terminal_1,
        dummy_component.terminal_2,
        "V",
    )
    voltage_2 = dummy_component.voltage("terminal_1", dummy_component.terminal_2, "V")
    voltage_3 = dummy_component.voltage(dummy_component.terminal_1, "terminal_2", "V")
    voltage_4 = dummy_component.voltage("terminal_1", "terminal_2", "V")

    assert voltage_1.from_terminal == dummy_component.terminal_1
    assert voltage_1.to_terminal == dummy_component.terminal_2
    assert voltage_2.from_terminal == dummy_component.terminal_1
    assert voltage_2.to_terminal == dummy_component.terminal_2
    assert voltage_3.from_terminal == dummy_component.terminal_1
    assert voltage_3.to_terminal == dummy_component.terminal_2
    assert voltage_4.from_terminal == dummy_component.terminal_1
    assert voltage_4.to_terminal == dummy_component.terminal_2


def test_voltage_sets_component_it_is_called_on_as_avoid(
    dummy_component: DummyComponent,
) -> None:
    voltage = dummy_component.voltage("terminal_1", "terminal_2", "V")

    assert voltage.component_to_avoid == dummy_component


def test_voltage_errors_if_terminals_are_the_same(
    dummy_component: DummyComponent,
) -> None:
    expected_message = (
        "The terminals specified through `from_terminal` and "
        "`to_terminal` are identical."
    )

    with pytest.raises(ValueError, match=expected_message):
        dummy_component.voltage(dummy_component.terminal_1, dummy_component.terminal_1)
    with pytest.raises(ValueError, match=expected_message):
        dummy_component.voltage("terminal_1", dummy_component.terminal_1)
    with pytest.raises(ValueError, match=expected_message):
        dummy_component.voltage(dummy_component.terminal_1, "terminal_1")
    with pytest.raises(ValueError, match=expected_message):
        dummy_component.voltage("terminal_1", "terminal_1")


def test_set_current_no_terminal_specified(
    dummy_component_mocked_terminals: DummyComponentMockedTerminals,
) -> None:
    current_label = "current label"

    dummy_component_mocked_terminals.set_current(current_label)

    dummy_component_mocked_terminals.cast_terminals[
        0
    ].set_current.assert_called_once_with(current_label)
    dummy_component_mocked_terminals.cast_terminals[1].set_current.assert_not_called()


def test_set_current_string_terminal_specified(
    dummy_component_mocked_terminals: DummyComponentMockedTerminals,
) -> None:
    current_label = "current label still"

    dummy_component_mocked_terminals.set_current(current_label, terminal="terminal_2")

    dummy_component_mocked_terminals.terminal_2.set_current.assert_called_once_with(
        current_label
    )
    dummy_component_mocked_terminals.terminal_1.set_current.assert_not_called()


def test_set_current_actual_terminal_specified(
    dummy_component_mocked_terminals: DummyComponentMockedTerminals,
) -> None:
    current_label = "current label again"

    dummy_component_mocked_terminals.set_current(
        current_label, terminal=dummy_component_mocked_terminals.terminal_2
    )

    dummy_component_mocked_terminals.terminal_2.set_current.assert_called_once_with(
        current_label
    )
    dummy_component_mocked_terminals.terminal_1.set_current.assert_not_called()


def test_set_current_passes_kwargs_on_to_set_current_on_terminal(
    dummy_component_mocked_terminals: DummyComponentMockedTerminals,
) -> None:
    current_label = "current label once more"

    dummy_component_mocked_terminals.set_current(current_label, out=True, below=True)

    dummy_component_mocked_terminals.cast_terminals[
        0
    ].set_current.assert_called_once_with(current_label, out=True, below=True)


def test_reset_current_no_terminal_specified(
    dummy_component_mocked_terminals: DummyComponentMockedTerminals,
) -> None:
    current_label = "current label"

    dummy_component_mocked_terminals.reset_current(current_label)

    dummy_component_mocked_terminals.cast_terminals[
        0
    ].reset_current.assert_called_once_with(current_label)
    dummy_component_mocked_terminals.cast_terminals[1].reset_current.assert_not_called()


def test_reset_current_string_terminal_specified(
    dummy_component_mocked_terminals: DummyComponentMockedTerminals,
) -> None:
    current_label = "current label still"

    dummy_component_mocked_terminals.reset_current(current_label, terminal="terminal_2")

    dummy_component_mocked_terminals.terminal_2.reset_current.assert_called_once_with(
        current_label
    )
    dummy_component_mocked_terminals.terminal_1.reset_current.assert_not_called()


def test_reset_current_actual_terminal_specified(
    dummy_component_mocked_terminals: DummyComponentMockedTerminals,
) -> None:
    current_label = "current label again"

    dummy_component_mocked_terminals.reset_current(
        current_label, terminal=dummy_component_mocked_terminals.terminal_2
    )

    dummy_component_mocked_terminals.terminal_2.reset_current.assert_called_once_with(
        current_label
    )
    dummy_component_mocked_terminals.terminal_1.reset_current.assert_not_called()


def test_reset_current_passes_kwargs_on_to_reset_current_on_terminal(
    dummy_component_mocked_terminals: DummyComponentMockedTerminals,
) -> None:
    current_label = "current label once more"

    dummy_component_mocked_terminals.reset_current(current_label, out=True, below=True)

    dummy_component_mocked_terminals.cast_terminals[
        0
    ].reset_current.assert_called_once_with(current_label, out=True, below=True)


def test_clear_current_no_terminal_specified(
    dummy_component_mocked_terminals: DummyComponentMockedTerminals,
) -> None:
    dummy_component_mocked_terminals.clear_current()

    dummy_component_mocked_terminals.cast_terminals[
        0
    ].clear_current.assert_called_once()
    dummy_component_mocked_terminals.cast_terminals[1].clear_current.assert_not_called()


def test_clear_current_string_terminal_specified(
    dummy_component_mocked_terminals: DummyComponentMockedTerminals,
) -> None:
    dummy_component_mocked_terminals.clear_current(terminal="terminal_2")

    dummy_component_mocked_terminals.terminal_2.clear_current.assert_called_once()
    dummy_component_mocked_terminals.terminal_1.clear_current.assert_not_called()


def test_clear_current_actual_terminal_specified(
    dummy_component_mocked_terminals: DummyComponentMockedTerminals,
) -> None:
    dummy_component_mocked_terminals.clear_current(
        terminal=dummy_component_mocked_terminals.terminal_2
    )

    dummy_component_mocked_terminals.terminal_2.clear_current.assert_called_once()
    dummy_component_mocked_terminals.terminal_1.clear_current.assert_not_called()


def test_get_or_check_terminal_non_belonging_terminal() -> None:
    component = DummyComponent()
    other_component = DummyComponent()

    with pytest.raises(
        ValueError, match="Passed terminal does not belong to this component."
    ):
        component._get_or_check_terminal(other_component.terminal_1)


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
    result = dummy_component._get_or_check_terminal(dummy_component.terminal_1)

    assert result == dummy_component.terminal_1


def test_get_or_check_terminal_valid_string(dummy_component: DummyComponent) -> None:
    result = dummy_component._get_or_check_terminal("terminal_1")

    assert result == dummy_component.terminal_1


def test_get_or_check_terminal_terminal_is_none(
    dummy_component: DummyComponent,
) -> None:
    result = dummy_component._get_or_check_terminal(None)

    assert result == dummy_component.terminals[0]
