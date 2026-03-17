"""Tests for Pin visibility state management."""

from unittest import mock

import manim as mn

from manim_eng.circuits.base.wire import WireBase
from manim_eng.components.base.pin import Pin


def test_is_visible_returns_false_when_no_wires_attached() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)

    assert pin.is_visible() is False


def test_register_attachment_adds_wire_but_does_not_make_pin_visible() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)

    pin.register_attachment(wire)

    assert wire in pin._attached_wires
    assert pin.is_visible() is False


def test_register_detachment_removes_wire_from_attached_wires() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    pin.register_attachment(wire)

    pin.register_detachment(wire)

    assert wire not in pin._attached_wires


def test_set_wire_visibility_true_makes_pin_visible() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    pin.register_attachment(wire)

    pin._set_wire_visibility(wire, True)

    assert pin.is_visible() is True


def test_set_wire_visibility_false_makes_pin_not_visible() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    pin.register_attachment(wire)
    pin._set_wire_visibility(wire, True)

    pin._set_wire_visibility(wire, False)

    assert pin.is_visible() is False


def test_is_visible_true_while_at_least_one_wire_still_visible() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)
    wire1 = mock.MagicMock(WireBase)
    wire2 = mock.MagicMock(WireBase)
    pin.register_attachment(wire1)
    pin.register_attachment(wire2)
    pin._set_wire_visibility(wire1, True)
    pin._set_wire_visibility(wire2, True)

    pin._set_wire_visibility(wire1, False)

    assert pin.is_visible() is True


def test_register_detachment_clears_wire_from_visible_wires() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    pin.register_attachment(wire)
    pin._set_wire_visibility(wire, True)

    pin.register_detachment(wire)

    assert pin.is_visible() is False
