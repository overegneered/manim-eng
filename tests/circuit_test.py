import pytest

from manim_eng import Circuit

from .utils.dummy_component import DummyComponent


def test_connect() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    circuit = Circuit(component_1, component_2)
    circuit_animated = Circuit(component_1, component_2)

    circuit.connect(component_1.left, component_2.right)
    circuit_animated.animate.connect(component_1.left, component_2.right)

    for submobjects in [circuit.wires.submobjects, circuit_animated.wires.submobjects]:
        assert len(submobjects) == 1
        assert submobjects[0].start == component_1.left
        assert submobjects[0].end == component_2.right


def test_connect_throws_value_error_if_terminals_are_identical(
    dummy_component: DummyComponent,
) -> None:
    circuit = Circuit(dummy_component)

    with pytest.raises(ValueError, match="`start` and `end` are identical"):
        circuit.connect(dummy_component.left, dummy_component.left)
    with pytest.raises(ValueError, match="`start` and `end` are identical"):
        circuit.animate.connect(dummy_component.left, dummy_component.left)


def test_connect_throws_error_if_terminals_do_not_belong_to_components_in_the_circuit(
    dummy_component: DummyComponent,
) -> None:
    circuit = Circuit()

    with pytest.raises(
        ValueError,
        match="At least one passed terminal does not "
        "belong to any component in this circuit",
    ):
        circuit.connect(dummy_component.left, dummy_component.right)
    with pytest.raises(
        ValueError,
        match="At least one passed terminal does not "
        "belong to any component in this circuit",
    ):
        circuit.animate.connect(dummy_component.left, dummy_component.right)


def test_disconnect() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    circuit = Circuit(component_1, component_2)
    circuit_animated = Circuit(component_1, component_2)
    for current_circuit in [circuit, circuit_animated]:
        current_circuit.connect(component_1.left, component_2.left).connect(
            component_1.left, component_2.right
        ).connect(component_1.right, component_2.right)

    circuit.disconnect(component_1, component_2.right)
    circuit_animated.animate.disconnect(component_1, component_2.right)

    for submobjects in [circuit.wires.submobjects, circuit_animated.wires.submobjects]:
        assert len(submobjects) == 1
        assert submobjects[0].start == component_1.left
        assert submobjects[0].end == component_2.left


def test_disconnect_throws_error_if_terminals_do_not_belong_to_components_in_circuit(
    dummy_component: DummyComponent,
) -> None:
    circuit = Circuit()

    with pytest.raises(
        ValueError,
        match="At least one passed terminal does not "
        "belong to any component in this circuit",
    ):
        circuit.disconnect(dummy_component.left, dummy_component.right)
    with pytest.raises(
        ValueError,
        match="At least one passed terminal does not "
        "belong to any component in this circuit",
    ):
        circuit.animate.disconnect(dummy_component.left, dummy_component.right)


def test_isolate() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    component_3 = DummyComponent()
    circuit = Circuit(component_1, component_2, component_3)
    circuit_animated = Circuit(component_1, component_2, component_3)
    for current_circuit in [circuit, circuit_animated]:
        current_circuit.connect(component_1.left, component_2.left).connect(
            component_1.left, component_2.right
        ).connect(component_1.right, component_2.right).connect(
            component_2.left, component_3.left
        ).connect(component_2.right, component_3.right)

    circuit.isolate(component_1, component_2.left)
    circuit_animated.animate.isolate(component_1, component_2.left)

    for submobjects in [circuit.wires.submobjects, circuit_animated.wires.submobjects]:
        assert len(submobjects) == 1
        assert submobjects[0].start == component_2.right
        assert submobjects[0].end == component_3.right


def test_isolate_throws_error_if_terminals_do_not_belong_to_components_in_the_circuit(
    dummy_component: DummyComponent,
) -> None:
    circuit = Circuit()

    with pytest.raises(
        ValueError,
        match="At least one passed terminal does not "
        "belong to any component in this circuit",
    ):
        circuit.isolate(dummy_component.left, dummy_component.right)
    with pytest.raises(
        ValueError,
        match="At least one passed terminal does not "
        "belong to any component in this circuit",
    ):
        circuit.animate.isolate(dummy_component.left, dummy_component.right)


def test_collapse_components_and_terminals_expands_components() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()

    terminals = Circuit._collapse_components_and_terminals_to_terminals(
        [component_1, component_2.right]
    )

    assert set(terminals) == {*component_1.pins, component_2.right}


def test_collapse_components_and_terminals_removes_duplicates() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    expected = [*component_1.pins, component_2.right]

    terminals = Circuit._collapse_components_and_terminals_to_terminals(
        [
            component_1,
            component_2.right,
            component_2.right,
            component_1.left,
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
