"""Tests for Pin visibility state management."""

from unittest import mock

import manim as mn
import pytest
from utils.pin_mocked import PinMockedParent

from manim_eng.circuits.base.wire import WireBase
from manim_eng.circuits.node import Node
from manim_eng.circuits.wire import ManualWire
from manim_eng.components.resistors import Resistor


def test_is_visible_returns_false_when_no_wire_attached() -> None:
    pin = PinMockedParent(mn.ORIGIN, mn.RIGHT)

    assert pin.is_visible() is False


def test_attach_wire_adds_wire_but_does_not_make_pin_visible() -> None:
    pin = PinMockedParent(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    wire.is_visible.return_value = False

    pin.attach_wire(wire)

    assert pin._attached_wire is wire
    assert pin.is_visible() is False


def test_detach_wire_removes_wire_from_attached_wire() -> None:
    pin = PinMockedParent(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    wire.is_visible.return_value = False
    pin.attach_wire(wire)

    pin.detach_wire()

    assert pin._attached_wire is None


def test_pin_is_visible_when_attached_wire_is_visible() -> None:
    pin = PinMockedParent(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    wire.is_visible.return_value = True
    pin.attach_wire(wire)

    assert pin.is_visible() is True


def test_pin_is_not_visible_when_attached_wire_is_hidden() -> None:
    pin = PinMockedParent(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    wire.is_visible.return_value = False
    pin.attach_wire(wire)

    assert pin.is_visible() is False


def test_detach_wire_makes_pin_not_visible() -> None:
    pin = PinMockedParent(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    wire.is_visible.return_value = True
    pin.attach_wire(wire)

    pin.detach_wire()

    assert pin.is_visible() is False


def test_attach_wire_raises_when_different_wire_already_attached() -> None:
    pin = PinMockedParent(mn.ORIGIN, mn.RIGHT)
    wire_a = mock.MagicMock(WireBase)
    wire_b = mock.MagicMock(WireBase)
    pin.attach_wire(wire_a)

    with pytest.raises(AttributeError):
        pin.attach_wire(wire_b)


# --------------------------------------------------------------------------------------
# get_network
# --------------------------------------------------------------------------------------


def test_get_network_isolated_pin_returns_only_itself() -> None:
    pin = PinMockedParent()
    pins, wires, nodes = pin.get_network()
    assert pins == {pin}
    assert wires == set()
    assert nodes == set()


def test_get_network_single_wire_returns_both_endpoints_and_wire() -> None:
    pin_a = PinMockedParent()
    pin_b = PinMockedParent()
    wire = ManualWire(pin_a, pin_b)
    pins, wires, nodes = pin_a.get_network()
    assert pins == {pin_a, pin_b}
    assert wires == {wire}
    assert nodes == set()


def test_get_network_linear_chain_of_two_wires_via_node() -> None:
    # pin_a -- wire_left -- node -- wire_right -- pin_b
    pin_a = PinMockedParent()
    pin_b = PinMockedParent()
    node = Node()
    wire_left = ManualWire(pin_a, node.left)
    wire_right = ManualWire(node.right, pin_b)

    pins, wires, nodes = pin_a.get_network()

    assert pins == {pin_a, pin_b, node.left, node.right}
    assert wires == {wire_left, wire_right}
    assert nodes == {node}


def test_get_network_t_junction_node_traversal() -> None:
    # Three wires meeting at a single node.
    #                      pin_c
    #                        |
    #                     wire_up
    #                        |
    # pin_a -- wire_left -- node -- wire_right -- pin_b
    pin_a = PinMockedParent()
    pin_b = PinMockedParent()
    pin_c = PinMockedParent()
    node = Node()
    wire1 = ManualWire(pin_a, node.left)
    wire2 = ManualWire(pin_b, node.right)
    wire3 = ManualWire(pin_c, node.up)

    pins, wires, nodes = pin_a.get_network()

    assert pins == {pin_a, pin_b, pin_c, node.left, node.right, node.up}
    assert wires == {wire1, wire2, wire3}
    assert nodes == {node}


def test_get_network_linear_chain_of_three_wires_via_two_nodes() -> None:
    # pin_a -- wire_1 -- node_1 -- wire_2 -- node_2 -- wire_3 -- pin_b
    pin_a = PinMockedParent()
    pin_b = PinMockedParent()
    node_1 = Node()
    node_2 = Node()
    n1l = node_1.left
    n1r = node_1.right
    n2l = node_2.left
    n2r = node_2.right
    wire_1 = ManualWire(pin_a, n1l)
    wire_2 = ManualWire(n1r, n2l)
    wire_3 = ManualWire(n2r, pin_b)
    pins, wires, nodes = pin_a.get_network()
    assert pins == {pin_a, pin_b, n1l, n1r, n2l, n2r}
    assert wires == {wire_1, wire_2, wire_3}
    assert nodes == {node_1, node_2}


def test_get_network_square_loop_topology() -> None:
    # n1 -- w12 -- n2
    #  |            |
    # w41          w23
    #  |            |
    # n4 -- w34 -- n3
    n1 = Node()
    n2 = Node()
    n3 = Node()
    n4 = Node()
    n1r = n1.right
    n2l = n2.left
    n2d = n2.down
    n3u = n3.up
    n3l = n3.left
    n4r = n4.right
    n4u = n4.up
    n1d = n1.down
    w12 = ManualWire(n1r, n2l)
    w23 = ManualWire(n2d, n3u)
    w34 = ManualWire(n3l, n4r)
    w41 = ManualWire(n4u, n1d)
    # Should complete without infinite loop.
    pins, wires, nodes = n1r.get_network()
    assert pins == {n1r, n2l, n2d, n3u, n3l, n4r, n4u, n1d}
    assert wires == {w12, w23, w34, w41}
    assert nodes == {n1, n2, n3, n4}


def test_get_network_node_with_unattached_pin_included() -> None:
    # Node has a left pin attached to a wire, and a right pin (sibling) that is not.
    pin_a = PinMockedParent()
    node = Node()
    pin_unattached = node.get(mn.UP + 2 * mn.LEFT)

    wire = ManualWire(pin_a, node.left)
    pins, wires, nodes = pin_a.get_network()
    # The unattached sibling node_right should be in the network.
    assert pins == {pin_a, node.left, pin_unattached}
    assert wires == {wire}
    assert nodes == {node}


def test_get_network_does_not_traverse_non_node_components() -> None:
    # pin_a -- wire_ab -- pin_b -- resistor - pin_c -- wire_cd -- pin_d
    resistor = Resistor()
    pin_a = PinMockedParent()
    pin_b = resistor.left
    pin_c = resistor.right
    pin_d = PinMockedParent()
    wire_ab = ManualWire(pin_a, pin_b)
    wire_cd = ManualWire(pin_c, pin_d)

    pins, wires, nodes = pin_a.get_network()
    assert pins == {pin_a, pin_b}
    assert wires == {wire_ab}
    assert nodes == set()
    pins, wires, nodes = pin_c.get_network()
    assert pins == {pin_c, pin_d}
    assert wires == {wire_cd}
    assert nodes == set()


# --------------------------------------------------------------------------------------
# get_connected_pins
# --------------------------------------------------------------------------------------


def test_get_connected_pins_isolated_pin_with_exclude_returns_empty_set() -> None:
    pin_a = PinMockedParent()
    assert pin_a.get_connected_pins(exclude_self=True) == set()


def test_get_connected_pins_t_junction_with_node_exclude() -> None:
    #                      pin_c
    #                        |
    #                     wire_up
    #                        |
    # pin_a -- wire_left -- node -- wire_right -- pin_b
    pin_a = PinMockedParent()
    pin_b = PinMockedParent()
    pin_c = PinMockedParent()
    node = Node()
    _wire1 = ManualWire(pin_a, node.left)
    _wire2 = ManualWire(pin_b, node.right)
    _wire3 = ManualWire(pin_c, node.up)

    assert pin_a.get_connected_pins(exclude_nodal_pins=True) == {pin_a, pin_b, pin_c}


def test_get_connected_pins_t_junction_with_node_exclude_and_self_exclude() -> None:
    #                      pin_c
    #                        |
    #                     wire_up
    #                        |
    # pin_a -- wire_left -- node -- wire_right -- pin_b
    pin_a = PinMockedParent()
    pin_b = PinMockedParent()
    pin_c = PinMockedParent()
    node = Node()
    _wire1 = ManualWire(pin_a, node.left)
    _wire2 = ManualWire(pin_b, node.right)
    _wire3 = ManualWire(pin_c, node.up)

    assert pin_a.get_connected_pins(exclude_self=True, exclude_nodal_pins=True) == {
        pin_b,
        pin_c,
    }
