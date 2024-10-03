import pytest
from manim_eng import Circuit

from .test_utils.dummy_component import DummyComponent


def test_connect() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    circuit = Circuit(component_1, component_2)
    circuit_animated = Circuit(component_1, component_2)

    circuit.connect(component_1.terminal_1, component_2.terminal_2)
    circuit_animated.animate.connect(component_1.terminal_1, component_2.terminal_2)

    for submobjects in [circuit.wires.submobjects, circuit_animated.wires.submobjects]:
        assert len(submobjects) == 1
        assert submobjects[0].from_terminal == component_1.terminal_1
        assert submobjects[0].to_terminal == component_2.terminal_2


def test_connect_throws_value_error_if_terminals_are_identical(
    dummy_component: DummyComponent,
) -> None:
    circuit = Circuit(dummy_component)

    with pytest.raises(
        ValueError, match="`from_terminal` and `to_terminal` are identical"
    ):
        circuit.connect(dummy_component.terminal_1, dummy_component.terminal_1)
    with pytest.raises(
        ValueError, match="`from_terminal` and `to_terminal` are identical"
    ):
        circuit.animate.connect(dummy_component.terminal_1, dummy_component.terminal_1)


def test_connect_throws_error_if_terminals_do_not_belong_to_components_in_the_circuit(
    dummy_component: DummyComponent,
) -> None:
    circuit = Circuit()

    with pytest.raises(
        ValueError,
        match="At least one passed terminal does not "
        "belong to any component in this circuit",
    ):
        circuit.connect(dummy_component.terminal_1, dummy_component.terminal_2)
    with pytest.raises(
        ValueError,
        match="At least one passed terminal does not "
        "belong to any component in this circuit",
    ):
        circuit.animate.connect(dummy_component.terminal_1, dummy_component.terminal_2)


def test_disconnect() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    circuit = Circuit(component_1, component_2)
    circuit_animated = Circuit(component_1, component_2)
    for current_circuit in [circuit, circuit_animated]:
        current_circuit.connect(component_1.terminal_1, component_2.terminal_1).connect(
            component_1.terminal_1, component_2.terminal_2
        ).connect(component_1.terminal_2, component_2.terminal_2)

    circuit.disconnect(component_1, component_2.terminal_2)
    circuit_animated.animate.disconnect(component_1, component_2.terminal_2)

    for submobjects in [circuit.wires.submobjects, circuit_animated.wires.submobjects]:
        assert len(submobjects) == 1
        assert submobjects[0].from_terminal == component_1.terminal_1
        assert submobjects[0].to_terminal == component_2.terminal_1


def test_disconnect_throws_error_if_terminals_do_not_belong_to_components_in_circuit(
    dummy_component: DummyComponent,
) -> None:
    circuit = Circuit()

    with pytest.raises(
        ValueError,
        match="At least one passed terminal does not "
        "belong to any component in this circuit",
    ):
        circuit.disconnect(dummy_component.terminal_1, dummy_component.terminal_2)
    with pytest.raises(
        ValueError,
        match="At least one passed terminal does not "
        "belong to any component in this circuit",
    ):
        circuit.animate.disconnect(
            dummy_component.terminal_1, dummy_component.terminal_2
        )


def test_isolate() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    component_3 = DummyComponent()
    circuit = Circuit(component_1, component_2, component_3)
    circuit_animated = Circuit(component_1, component_2, component_3)
    for current_circuit in [circuit, circuit_animated]:
        current_circuit.connect(component_1.terminal_1, component_2.terminal_1).connect(
            component_1.terminal_1, component_2.terminal_2
        ).connect(component_1.terminal_2, component_2.terminal_2).connect(
            component_2.terminal_1, component_3.terminal_1
        ).connect(component_2.terminal_2, component_3.terminal_2)

    circuit.isolate(component_1, component_2.terminal_1)
    circuit_animated.animate.isolate(component_1, component_2.terminal_1)

    for submobjects in [circuit.wires.submobjects, circuit_animated.wires.submobjects]:
        assert len(submobjects) == 1
        assert submobjects[0].from_terminal == component_2.terminal_2
        assert submobjects[0].to_terminal == component_3.terminal_2


def test_isolate_throws_error_if_terminals_do_not_belong_to_components_in_the_circuit(
    dummy_component: DummyComponent,
) -> None:
    circuit = Circuit()

    with pytest.raises(
        ValueError,
        match="At least one passed terminal does not "
        "belong to any component in this circuit",
    ):
        circuit.isolate(dummy_component.terminal_1, dummy_component.terminal_2)
    with pytest.raises(
        ValueError,
        match="At least one passed terminal does not "
        "belong to any component in this circuit",
    ):
        circuit.animate.isolate(dummy_component.terminal_1, dummy_component.terminal_2)


def test_collapse_components_and_terminals_expands_components() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()

    terminals = Circuit._collapse_components_and_terminals_to_terminals(
        [component_1, component_2.terminal_2]
    )

    assert set(terminals) == {*component_1.terminals, component_2.terminal_2}


def test_collapse_components_and_terminals_removes_duplicates() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    expected = [*component_1.terminals, component_2.terminal_2]

    terminals = Circuit._collapse_components_and_terminals_to_terminals(
        [
            component_1,
            component_2.terminal_2,
            component_2.terminal_2,
            component_1.terminal_1,
        ]
    )

    # Check the length to make sure that the set comparison (done because the order of
    # the entries is not important) doesn't hide the removal of duplicates here rather
    # than in the method under test
    assert len(terminals) == len(expected)
    assert set(terminals) == set(expected)


def test_collapse_components_and_terminals_returns_empty_list_with_empty_input() -> (
    None
):
    terminals = Circuit._collapse_components_and_terminals_to_terminals([])

    assert terminals == []
