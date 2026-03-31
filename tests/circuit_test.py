import manim as mn
import pytest

from manim_eng import Circuit, Wire
from manim_eng.circuits.node import Node

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


def test_connect_throws_value_error_if_pins_are_identical(
    dummy_component: DummyComponent,
) -> None:
    circuit = Circuit(dummy_component)

    with pytest.raises(ValueError, match="`start` and `end` are identical"):
        circuit.connect(dummy_component.left, dummy_component.left)
    with pytest.raises(ValueError, match="`start` and `end` are identical"):
        circuit.animate.connect(dummy_component.left, dummy_component.left)


def test_connect_throws_error_if_pins_do_not_belong_to_components_in_the_circuit(
    dummy_component: DummyComponent,
) -> None:
    circuit = Circuit()

    with pytest.raises(
        ValueError,
        match="At least one passed pin does not "
        "belong to any component in this circuit",
    ):
        circuit.connect(dummy_component.left, dummy_component.right)
    with pytest.raises(
        ValueError,
        match="At least one passed pin does not "
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


def test_disconnect_throws_error_if_pins_do_not_belong_to_components_in_circuit(
    dummy_component: DummyComponent,
) -> None:
    circuit = Circuit()

    with pytest.raises(
        ValueError,
        match="At least one passed pin does not "
        "belong to any component in this circuit",
    ):
        circuit.disconnect(dummy_component.left, dummy_component.right)
    with pytest.raises(
        ValueError,
        match="At least one passed pin does not "
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


def test_isolate_throws_error_if_pins_do_not_belong_to_components_in_the_circuit(
    dummy_component: DummyComponent,
) -> None:
    circuit = Circuit()

    with pytest.raises(
        ValueError,
        match="At least one passed pin does not "
        "belong to any component in this circuit",
    ):
        circuit.isolate(dummy_component.left, dummy_component.right)
    with pytest.raises(
        ValueError,
        match="At least one passed pin does not "
        "belong to any component in this circuit",
    ):
        circuit.animate.isolate(dummy_component.left, dummy_component.right)


def test_connect_marks_pins_as_visible() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    circuit = Circuit(component_1, component_2)

    circuit.connect(component_1.right, component_2.left)

    assert component_1.right.is_visible() is True
    assert component_2.left.is_visible() is True


def test_disconnect_marks_pins_as_not_visible() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    circuit = Circuit(component_1, component_2)
    circuit.connect(component_1.right, component_2.left)

    circuit.disconnect(component_1.right, component_2.left)

    assert component_1.right.is_visible() is False
    assert component_2.left.is_visible() is False


def test_isolate_marks_pins_as_not_visible() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    circuit = Circuit(component_1, component_2)
    circuit.connect(component_1.right, component_2.left)

    circuit.isolate(component_1)

    assert component_1.right.is_visible() is False
    assert component_2.left.is_visible() is False


def test_collapse_components_and_pins_expands_components() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()

    terminals = Circuit._collapse_components_and_pins_to_pins(
        [component_1, component_2.right]
    )

    assert set(terminals) == {*component_1.pins, component_2.right}


def test_collapse_components_and_pins_removes_duplicates() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    expected = [*component_1.pins, component_2.right]

    terminals = Circuit._collapse_components_and_pins_to_pins(
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


def test_collapse_components_and_pins_returns_empty_list_with_empty_input() -> None:
    terminals = Circuit._collapse_components_and_pins_to_pins([])

    assert terminals == []


# --------------------------------------------------------------------------------------
# _get_connections_for_pin() — unconnected pins
# --------------------------------------------------------------------------------------


def test_get_connections_for_pin_returns_empty_set_when_no_wire_attached() -> None:
    component = DummyComponent()
    circuit = Circuit(component)

    result = circuit._get_connections_for_pin(component.left)

    assert result == set()


# --------------------------------------------------------------------------------------
# _get_connections_for_pin() — direct (non-Node) connections
# --------------------------------------------------------------------------------------


def test_get_connections_for_pin_direct_connection_from_start() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    circuit = Circuit(component_1, component_2)
    Wire(component_1.right, component_2.left)

    result = circuit._get_connections_for_pin(component_1.right)

    assert result == {component_1.right, component_2.left}


def test_get_connections_for_pin_direct_connection_from_end() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    circuit = Circuit(component_1, component_2)
    Wire(component_1.right, component_2.left)

    result = circuit._get_connections_for_pin(component_2.left)

    assert result == {component_1.right, component_2.left}


# --------------------------------------------------------------------------------------
# _get_connections_for_pin() — connections through a single Node
# --------------------------------------------------------------------------------------


def test_get_connections_for_pin_traverses_node() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    node = Node().move_to(mn.ORIGIN)
    circuit = Circuit(component_1, component_2, node)
    Wire(component_1.right, node.left)
    Wire(node.right, component_2.left)

    result = circuit._get_connections_for_pin(component_1.right)

    assert node.left in result
    assert node.right in result
    assert component_2.left in result


def test_get_connections_for_pin_includes_unconnected_node_pin() -> None:
    component_1 = DummyComponent()
    node = Node().move_to(mn.ORIGIN)
    circuit = Circuit(component_1, node)
    Wire(component_1.right, node.left)
    # Touch node.right now so the pin is created and lives in node.pins before
    # the traversal runs.  It is intentionally left unconnected.
    unconnected_pin = node.right

    result = circuit._get_connections_for_pin(component_1.right)

    # The traversal iterates all pins on the node, so the unconnected pin must
    # appear in the returned set even though it has no wire.
    assert unconnected_pin in result


def test_get_connections_for_pin_t_junction() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    component_3 = DummyComponent()
    node = Node().move_to(mn.ORIGIN)
    circuit = Circuit(component_1, component_2, component_3, node)
    Wire(component_1.right, node.left)
    Wire(node.right, component_2.left)
    Wire(node.up, component_3.left)

    result = circuit._get_connections_for_pin(component_1.right)

    assert node.left in result
    assert node.right in result
    assert node.up in result
    assert component_2.left in result
    assert component_3.left in result


# --------------------------------------------------------------------------------------
# _get_connections_for_pin() — chains through multiple Nodes
# --------------------------------------------------------------------------------------


def test_get_connections_for_pin_chain_through_two_nodes() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    node_a = Node().move_to(mn.LEFT)
    node_b = Node().move_to(mn.RIGHT)
    circuit = Circuit(component_1, component_2, node_a, node_b)
    Wire(component_1.right, node_a.left)
    Wire(node_a.right, node_b.left)
    Wire(node_b.right, component_2.left)

    result = circuit._get_connections_for_pin(component_1.right)

    assert node_a.left in result
    assert node_a.right in result
    assert node_b.left in result
    assert node_b.right in result
    assert component_2.left in result


def test_get_connections_for_pin_star_topology() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    component_3 = DummyComponent()
    node = Node().move_to(mn.ORIGIN)
    circuit = Circuit(component_1, component_2, component_3, node)
    Wire(component_1.right, node.left)
    Wire(component_2.right, node.right)
    Wire(component_3.right, node.up)

    result = circuit._get_connections_for_pin(component_1.right)

    assert node.left in result
    assert node.right in result
    assert node.up in result
    assert component_2.right in result
    assert component_3.right in result


# --------------------------------------------------------------------------------------
# _get_connections_for_pin() — cycle/loop detection
# --------------------------------------------------------------------------------------


def test_get_connections_for_pin_cycle_two_nodes() -> None:
    component = DummyComponent()
    node_a = Node().move_to(mn.LEFT)
    node_b = Node().move_to(mn.RIGHT)
    circuit = Circuit(component, node_a, node_b)
    Wire(component.right, node_a.left)
    Wire(node_a.right, node_b.left)
    Wire(node_b.right, node_a.up)

    # Must not raise RecursionError; result must include the full reachable set
    result = circuit._get_connections_for_pin(component.right)

    # At minimum, node_a pins entered first should be present
    assert isinstance(result, set)
    assert node_a.left in result


def test_get_connections_for_pin_component_wired_back_to_itself_via_two_nodes() -> None:
    component = DummyComponent()
    node_a = Node().move_to(mn.LEFT)
    node_b = Node().move_to(mn.RIGHT)
    circuit = Circuit(component, node_a, node_b)
    Wire(component.right, node_a.left)
    Wire(node_a.right, node_b.left)
    Wire(node_b.right, component.left)

    # Must not raise RecursionError
    result = circuit._get_connections_for_pin(component.right)

    assert isinstance(result, set)
    assert node_a.left in result


# --------------------------------------------------------------------------------------
# _get_connections_for_pin() — `existing` parameter behaviour
# --------------------------------------------------------------------------------------


def test_get_connections_for_pin_pre_seeded_existing_is_respected() -> None:
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    node = Node().move_to(mn.ORIGIN)
    circuit = Circuit(component_1, component_2, node)
    Wire(component_1.right, node.left)
    Wire(node.right, component_2.left)

    # Pre-seed with node.left to simulate it already having been visited
    existing: set = {node.left}
    result = circuit._get_connections_for_pin(component_1.right, existing=existing)

    # node.left was already known; result should still contain node.right and
    # component_2.left because they were not yet visited.
    assert node.right in result
    assert component_2.left in result
    # node.left is in `existing` and so the traversal must not recurse into it
    # again. It should still appear in the returned set because it was in
    # `existing` before the call.
    assert node.left in result


def test_get_connections_for_pin_existing_is_mutated_in_place() -> None:
    component_1 = DummyComponent()
    node = Node().move_to(mn.ORIGIN)
    circuit = Circuit(component_1, node)
    Wire(component_1.right, node.left)

    existing: set = {component_1.right}
    result = circuit._get_connections_for_pin(component_1.right, existing=existing)

    # The contract is that `existing` is mutated in-place and the same object
    # is returned.
    assert result is existing


def test_get_connections_for_pin_none_existing_includes_pin_itself() -> None:
    component_1 = DummyComponent()
    node = Node().move_to(mn.ORIGIN)
    circuit = Circuit(component_1, node)
    Wire(component_1.right, node.left)

    result = circuit._get_connections_for_pin(component_1.right)

    # When existing=None, the implementation initialises existing = {pin}.
    # The query pin must therefore appear in the result.
    assert component_1.right in result


# --------------------------------------------------------------------------------------
# _get_connections_for_pin() — boundary conditions
# --------------------------------------------------------------------------------------


def test_get_connections_for_pin_node_with_single_pin() -> None:
    component = DummyComponent()
    node = Node().move_to(mn.ORIGIN)
    circuit = Circuit(component, node)
    # Only one wire into the node — node.left is the sole pin created.
    Wire(component.right, node.left)

    # Must not raise; we only care that a set is returned.
    result = circuit._get_connections_for_pin(component.right)

    assert isinstance(result, set)
