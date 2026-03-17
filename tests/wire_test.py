import manim as mn
import pytest

from manim_eng import ManualWire, Wire
from manim_eng.components.base.pin import Pin


def test_wire_throws_value_error_if_pins_are_identical() -> None:
    pin = Pin(mn.ORIGIN, mn.LEFT)

    with pytest.raises(
        ValueError,
        match=r"`start` and `end` are identical\. "
        r"Wires must have different pins at each end\.",
    ):
        Wire(pin, pin)


def test_manual_wire_throws_value_error_if_pins_are_identical() -> None:
    pin = Pin(mn.ORIGIN, mn.LEFT)

    with pytest.raises(
        ValueError,
        match=r"`start` and `end` are identical\. "
        r"Wires must have different pins at each end\.",
    ):
        ManualWire(pin, pin, [])
