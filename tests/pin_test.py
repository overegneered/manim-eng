"""Tests for Pin visibility state management."""

from unittest import mock

import manim as mn
import pytest

from manim_eng.circuits.base.wire import WireBase
from manim_eng.components.base.pin import Pin


def test_is_visible_returns_false_when_no_wire_attached() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)

    assert pin.is_visible() is False


def test_attach_wire_adds_wire_but_does_not_make_pin_visible() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    wire.is_visible.return_value = False

    pin.attach_wire(wire)

    assert pin._attached_wire is wire
    assert pin.is_visible() is False


def test_detach_wire_removes_wire_from_attached_wire() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    wire.is_visible.return_value = False
    pin.attach_wire(wire)

    pin.detach_wire()

    assert pin._attached_wire is None


def test_pin_is_visible_when_attached_wire_is_visible() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    wire.is_visible.return_value = True
    pin.attach_wire(wire)

    assert pin.is_visible() is True


def test_pin_is_not_visible_when_attached_wire_is_hidden() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    wire.is_visible.return_value = False
    pin.attach_wire(wire)

    assert pin.is_visible() is False


def test_detach_wire_makes_pin_not_visible() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)
    wire = mock.MagicMock(WireBase)
    wire.is_visible.return_value = True
    pin.attach_wire(wire)

    pin.detach_wire()

    assert pin.is_visible() is False


def test_attach_wire_raises_when_different_wire_already_attached() -> None:
    pin = Pin(mn.ORIGIN, mn.RIGHT)
    wire_a = mock.MagicMock(WireBase)
    wire_b = mock.MagicMock(WireBase)
    pin.attach_wire(wire_a)

    with pytest.raises(AttributeError):
        pin.attach_wire(wire_b)
