"""Tests for the Network utility class."""

import manim as mn
import manim.typing as mnt
import numpy as np
import pytest

from manim_eng import ManualWire
from manim_eng.circuits.network import Network
from manim_eng.circuits.node import Node
from tests.utils.dummy_component import DummyComponent
from tests.utils.pin_mocked import PinMockedParent


def _wire_from_vertices(vertices: list[mnt.Point3D]) -> ManualWire:
    start = PinMockedParent(vertices[0], mn.RIGHT)
    end = PinMockedParent(vertices[-1], mn.RIGHT)
    corners = vertices[1:-1]
    return ManualWire(start, end, corners)


# ---------------------------------------------------------------------------
# Construction from Pin
# ---------------------------------------------------------------------------


def test_init_from_unconnected_pin_contains_only_that_pin() -> None:
    pin = PinMockedParent()

    net = Network(pin)

    assert net.pins == {pin}
    assert net.wires == set()
    assert net.nodes == set()


def test_init_from_pin_with_wire_follows_wire_to_other_end() -> None:
    pin_a = PinMockedParent(mn.LEFT, mn.LEFT)
    pin_b = PinMockedParent(mn.RIGHT, mn.RIGHT)
    wire = ManualWire(pin_a, pin_b)

    net = Network(pin_a)

    assert net.pins == {pin_a, pin_b}
    assert net.wires == {wire}
    assert net.nodes == set()


def test_init_from_pin_traverses_chain_of_two_wires() -> None:
    # Each pin can only hold one wire, so the mid-chain junction is a Node.
    pin_a = PinMockedParent(mn.LEFT * 2, mn.RIGHT)
    node_b = Node()
    pin_c = PinMockedParent(mn.RIGHT * 2, mn.LEFT)
    wire1 = ManualWire(pin_a, node_b.left)
    wire2 = ManualWire(node_b.right, pin_c)

    net = Network(pin_a)

    assert pin_a in net.pins
    assert pin_c in net.pins
    assert wire1 in net.wires
    assert wire2 in net.wires
    assert node_b in net.nodes


def test_init_from_pin_does_not_cross_component_boundary() -> None:
    comp = DummyComponent()
    ext_pin = PinMockedParent(mn.LEFT * 2, mn.RIGHT)
    wire = ManualWire(ext_pin, comp.left)

    net = Network(ext_pin)

    assert net.pins == {ext_pin, comp.left}
    assert comp.right not in net.pins
    assert net.wires == {wire}
    assert net.nodes == set()


# ---------------------------------------------------------------------------
# Construction from WireBase
# ---------------------------------------------------------------------------


def test_init_from_wire_uses_start_pin_as_entry_point() -> None:
    pin_a = PinMockedParent(mn.LEFT, mn.LEFT)
    pin_b = PinMockedParent(mn.RIGHT, mn.RIGHT)
    wire = ManualWire(pin_a, pin_b)

    net_from_wire = Network(wire)
    net_from_start = Network(wire.start)

    assert net_from_wire.pins == net_from_start.pins
    assert net_from_wire.wires == net_from_start.wires
    assert net_from_wire.nodes == net_from_start.nodes


def test_init_from_wire_with_chain_traverses_all_reachable_elements() -> None:
    pin_a = PinMockedParent(mn.LEFT * 3, mn.RIGHT)
    node1 = Node()
    node2 = Node()
    pin_d = PinMockedParent(mn.RIGHT * 3, mn.LEFT)

    wire1 = ManualWire(pin_a, node1.left)
    wire2 = ManualWire(node1.right, node2.left)
    wire3 = ManualWire(node2.right, pin_d)

    net = Network(wire2)

    assert net.pins == {pin_a, node1.left, node1.right, node2.left, node2.right, pin_d}
    assert net.wires == {wire1, wire2, wire3}
    assert net.nodes == {node1, node2}


# ---------------------------------------------------------------------------
# Construction from Node
# ---------------------------------------------------------------------------


def test_init_from_node_with_no_pins_contains_only_that_node() -> None:
    node = Node()

    net = Network(node)

    assert net.pins == set()
    assert net.wires == set()
    assert net.nodes == {node}


def test_init_from_node_with_pins_enters_via_first_pin() -> None:
    node = Node()
    _ = node.left
    _ = node.right

    net = Network(node)

    assert node.left in net.pins
    assert node.right in net.pins
    assert net.wires == set()
    assert net.nodes == {node}


def test_init_from_node_with_wired_pin_follows_wire() -> None:
    node = Node()
    ext_pin = PinMockedParent(mn.LEFT * 2, mn.RIGHT)
    wire = ManualWire(ext_pin, node.left)

    net = Network(node)

    assert ext_pin in net.pins
    assert node.left in net.pins
    assert wire in net.wires
    assert node in net.nodes


# ---------------------------------------------------------------------------
# Construction: TypeError for invalid start
# ---------------------------------------------------------------------------


def test_init_raises_type_error_for_invalid_start_type() -> None:
    with pytest.raises(TypeError, match="`start` must be"):
        Network(42)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Construction: exclude_nodal_pins flag
# ---------------------------------------------------------------------------


def test_exclude_nodal_pins_false_includes_all_node_sibling_pins() -> None:
    node = Node()
    ext_pin = PinMockedParent(mn.LEFT * 2, mn.RIGHT)
    _wire = ManualWire(ext_pin, node.left)
    _ = node.right  # sibling with no wire

    net = Network(ext_pin, exclude_nodal_pins=False)

    assert node.left in net.pins
    assert node.right in net.pins


def test_exclude_nodal_pins_true_omits_sibling_node_pins_from_pins_set() -> None:
    node = Node()
    ext_pin = PinMockedParent(mn.LEFT * 2, mn.RIGHT)
    _wire = ManualWire(ext_pin, node.left)
    _ = node.right  # sibling with no wire

    net = Network(ext_pin, exclude_nodal_pins=True)

    assert node.right not in net.pins


def test_exclude_nodal_pins_true_still_traverses_through_node() -> None:
    # Traversal continues through node siblings even when they are excluded from pins;
    # wires on those siblings are followed and their far-end component pins are
    # collected.
    node = Node()
    ext_pin_a = PinMockedParent(mn.LEFT * 2, mn.RIGHT)
    ext_pin_b = PinMockedParent(mn.RIGHT * 2, mn.LEFT)
    _wire1 = ManualWire(ext_pin_a, node.left)
    _wire2 = ManualWire(node.right, ext_pin_b)

    net = Network(ext_pin_a, exclude_nodal_pins=True)

    assert ext_pin_b in net.pins


def test_exclude_nodal_pins_true_still_adds_node_to_nodes_set() -> None:
    node = Node()
    ext_pin = PinMockedParent(mn.LEFT * 2, mn.RIGHT)
    _wire = ManualWire(ext_pin, node.left)

    net = Network(ext_pin, exclude_nodal_pins=True)

    assert node in net.nodes


# ---------------------------------------------------------------------------
# __init__: unwired node pins are included
# ---------------------------------------------------------------------------


def test_nodal_pin_with_no_wire_is_included_in_pins() -> None:
    node = Node()
    ext_pin = PinMockedParent(mn.LEFT * 2, mn.RIGHT)
    _wire = ManualWire(ext_pin, node.left)
    _ = node.right  # no wire attached

    net = Network(ext_pin)

    assert node.right in net.pins


# ---------------------------------------------------------------------------
# __init__: Node chains and loops
# ---------------------------------------------------------------------------


def test_network_from_pin_in_cycle_terminates() -> None:
    # node1.right → wire1 → node2.left and node2.right → wire2 → node1.left
    node1 = Node()
    node2 = Node()
    wire1 = ManualWire(node1.right, node2.left)
    wire2 = ManualWire(node2.right, node1.left)

    net = Network(node1.right)

    assert net.wires == {wire1, wire2}
    assert net.nodes == {node1, node2}
    assert net.pins == {node1.right, node1.left, node2.left, node2.right}


def test_network_traverses_chain_of_nodes() -> None:
    pin_a = PinMockedParent(mn.LEFT * 3, mn.RIGHT)
    node1 = Node()
    node2 = Node()
    pin_b = PinMockedParent(mn.RIGHT * 3, mn.LEFT)

    wire1 = ManualWire(pin_a, node1.left)
    wire2 = ManualWire(node1.right, node2.left)
    wire3 = ManualWire(node2.right, pin_b)

    net = Network(pin_a)

    assert net.nodes == {node1, node2}
    assert net.wires == {wire1, wire2, wire3}
    assert pin_a in net.pins
    assert pin_b in net.pins


# ---------------------------------------------------------------------------
# get_point_closest_to
# ---------------------------------------------------------------------------


def test_get_point_closest_to_with_single_wire_returns_closest_wire_point() -> None:
    wire = _wire_from_vertices([np.array([-1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])])
    net = Network(wire)

    result = net.get_point_closest_to(np.array([0.0, 1.0, 0.0]))

    assert result == pytest.approx([0.0, 0.0, 0.0])


def test_get_point_closest_to_with_multiple_wires_selects_globally_closest() -> None:
    wire_near = _wire_from_vertices(
        [np.array([-1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])]
    )
    wire_far = _wire_from_vertices(
        [np.array([-1.0, 5.0, 0.0]), np.array([1.0, 5.0, 0.0])]
    )
    net = Network(wire_near)
    net.wires.add(wire_far)

    result = net.get_point_closest_to(np.array([0.0, 1.0, 0.0]))

    assert result == pytest.approx([0.0, 0.0, 0.0])


def test_get_point_closest_to_no_wires_single_pin_returns_pin_base() -> None:
    pin = PinMockedParent(np.array([3.0, 4.0, 0.0]), mn.RIGHT)
    net = Network(pin)

    result = net.get_point_closest_to(np.array([0.0, 0.0, 0.0]))

    assert result == pytest.approx(pin.base)


def test_get_point_closest_to_no_wires_no_pins_empty_node_returns_node_center() -> None:
    node = Node()
    net = Network(node)

    result = net.get_point_closest_to(np.array([0.0, 0.0, 0.0]))

    assert result == pytest.approx(node.get_center())


def test_get_point_closest_to_empty_network_raises_value_error() -> None:
    node = Node()
    net = Network(node)
    net.nodes.clear()

    with pytest.raises(ValueError, match="empty"):
        net.get_point_closest_to(np.array([0.0, 0.0, 0.0]))


def test_get_point_closest_to_accepts_pin_argument() -> None:
    wire = _wire_from_vertices([np.array([-1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])])
    net = Network(wire)
    query_pin = PinMockedParent(np.array([0.0, 2.0, 0.0]), mn.UP)

    result_via_pin = net.get_point_closest_to(query_pin)
    result_via_tip = net.get_point_closest_to(query_pin.tip)

    assert result_via_pin == pytest.approx(result_via_tip)


# ---------------------------------------------------------------------------
# get_closest_points_with: WireBase overload
# ---------------------------------------------------------------------------


def test_get_closest_points_with_wire_return_order_self_first() -> None:
    net_wire = _wire_from_vertices(
        [np.array([0.0, 0.0, 0.0]), np.array([2.0, 0.0, 0.0])]
    )
    other_wire = _wire_from_vertices(
        [np.array([0.0, 2.0, 0.0]), np.array([2.0, 2.0, 0.0])]
    )
    net = Network(net_wire)

    p, q = net.get_closest_points_with(other_wire)

    assert p[1] == pytest.approx(0.0)
    assert q[1] == pytest.approx(2.0)


def test_get_closest_points_with_wire_finds_global_minimum_over_all_wires() -> None:
    wire_near = _wire_from_vertices(
        [np.array([0.0, 0.0, 0.0]), np.array([2.0, 0.0, 0.0])]
    )
    wire_far = _wire_from_vertices(
        [np.array([0.0, 10.0, 0.0]), np.array([2.0, 10.0, 0.0])]
    )
    other_wire = _wire_from_vertices(
        [np.array([0.0, 1.0, 0.0]), np.array([2.0, 1.0, 0.0])]
    )
    net = Network(wire_near)
    net.wires.add(wire_far)

    p, q = net.get_closest_points_with(other_wire)

    assert p[1] == pytest.approx(0.0)
    assert q[1] == pytest.approx(1.0)


def test_get_closest_points_with_wire_no_wires_pin_only_uses_pin_base() -> None:
    pin = PinMockedParent(np.array([0.0, 0.0, 0.0]), mn.RIGHT)
    other_wire = _wire_from_vertices(
        [np.array([1.0, 1.0, 0.0]), np.array([3.0, 1.0, 0.0])]
    )
    net = Network(pin)

    p, q = net.get_closest_points_with(other_wire)

    assert p == pytest.approx(pin.base)
    assert q == pytest.approx(other_wire.get_point_closest_to(pin.base))


def test_get_closest_points_with_wire_no_wires_no_pins_just_node_uses_node_center() -> (
    None
):
    node = Node()
    net = Network(node)
    other_wire = _wire_from_vertices(
        [np.array([1.0, 1.0, 0.0]), np.array([3.0, 1.0, 0.0])]
    )

    p, q = net.get_closest_points_with(other_wire)

    assert p == pytest.approx(node.get_center())
    assert q == pytest.approx(other_wire.get_point_closest_to(node.get_center()))


def test_get_closest_points_with_wire_empty_network_raises_value_error() -> None:
    node = Node()
    net = Network(node)
    net.nodes.clear()
    other_wire = _wire_from_vertices(
        [np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])]
    )

    with pytest.raises(ValueError, match="empty"):
        net.get_closest_points_with(other_wire)


# ---------------------------------------------------------------------------
# get_closest_points_with: Network overload
# ---------------------------------------------------------------------------


def test_get_closest_points_with_network_return_order() -> None:
    wire_a = _wire_from_vertices([np.array([0.0, 0.0, 0.0]), np.array([2.0, 0.0, 0.0])])
    wire_b = _wire_from_vertices([np.array([0.0, 3.0, 0.0]), np.array([2.0, 3.0, 0.0])])
    net_a = Network(wire_a)
    net_b = Network(wire_b)

    p, q = net_a.get_closest_points_with(net_b)

    assert p[1] == pytest.approx(0.0)
    assert q[1] == pytest.approx(3.0)


def test_get_closest_points_with_network_symmetry() -> None:
    wire_a = _wire_from_vertices([np.array([0.0, 0.0, 0.0]), np.array([2.0, 0.0, 0.0])])
    wire_b = _wire_from_vertices([np.array([0.0, 3.0, 0.0]), np.array([2.0, 3.0, 0.0])])
    net_a = Network(wire_a)
    net_b = Network(wire_b)

    p, q = net_a.get_closest_points_with(net_b)
    p2, q2 = net_b.get_closest_points_with(net_a)

    assert p == pytest.approx(q2)
    assert q == pytest.approx(p2)


def test_get_closest_points_with_network_crossing_wires() -> None:
    h_wire = _wire_from_vertices(
        [np.array([-1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])]
    )
    v_wire = _wire_from_vertices(
        [np.array([0.0, -1.0, 0.0]), np.array([0.0, 1.0, 0.0])]
    )
    net_h = Network(h_wire)
    net_v = Network(v_wire)

    p, q = net_h.get_closest_points_with(net_v)

    assert p == pytest.approx([0.0, 0.0, 0.0])
    assert q == pytest.approx([0.0, 0.0, 0.0])


def test_get_closest_points_with_network_pin_only_uses_pin_base_for_self() -> None:
    pin = PinMockedParent(np.array([0.0, 0.0, 0.0]), mn.RIGHT)
    wire = _wire_from_vertices([np.array([1.0, 1.0, 0.0]), np.array([3.0, 1.0, 0.0])])
    net_pin = Network(pin)
    net_wire = Network(wire)

    p, _ = net_pin.get_closest_points_with(net_wire)

    assert p == pytest.approx(pin.base)


def test_get_closest_points_with_network_pin_only_uses_pin_base_for_other() -> None:
    pin = PinMockedParent(np.array([3.0, 0.0, 0.0]), mn.LEFT)
    wire = _wire_from_vertices([np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])])
    net_wire = Network(wire)
    net_pin = Network(pin)

    _, q = net_wire.get_closest_points_with(net_pin)

    assert q == pytest.approx(pin.base)


# ---------------------------------------------------------------------------
# __iter__
# ---------------------------------------------------------------------------


def test_iter_yields_pins_wires_nodes_in_order() -> None:
    pin_a = PinMockedParent(mn.LEFT, mn.LEFT)
    pin_b = PinMockedParent(mn.RIGHT, mn.RIGHT)
    wire = ManualWire(pin_a, pin_b)
    net = Network(pin_a)

    pins, wires, nodes = net

    assert pins == {pin_a, pin_b}
    assert wires == {wire}
    assert nodes == set()


def test_iter_yields_sets_not_copies() -> None:
    pin_a = PinMockedParent(mn.LEFT, mn.LEFT)
    pin_b = PinMockedParent(mn.RIGHT, mn.RIGHT)
    _wire = ManualWire(pin_a, pin_b)
    net = Network(pin_a)

    pins, wires, nodes = net

    assert pins is net.pins
    assert wires is net.wires
    assert nodes is net.nodes
