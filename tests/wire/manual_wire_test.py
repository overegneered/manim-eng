import manim as mn
import numpy as np
import pytest
from utils.pin_mocked import PinMockedParent

from manim_eng import ManualWire, Wire

# --------------------------------------------------------------------------------------
# __init__
# --------------------------------------------------------------------------------------


def test_wire_throws_value_error_if_pins_are_identical() -> None:
    pin = PinMockedParent(mn.ORIGIN, mn.LEFT)

    with pytest.raises(
        ValueError,
        match=r"`start` and `end` are identical\. "
        r"Wires must have different pins at each end\.",
    ):
        Wire(pin, pin)


def test_manual_wire_throws_value_error_if_pins_are_identical() -> None:
    pin = PinMockedParent(mn.ORIGIN, mn.LEFT)

    with pytest.raises(
        ValueError,
        match=r"`start` and `end` are identical\. "
        r"Wires must have different pins at each end\.",
    ):
        ManualWire(pin, pin, [])


# --------------------------------------------------------------------------------------
# on_split
# --------------------------------------------------------------------------------------

# helpers ------------------------------------------------------------------------------


def _make_no_corner_wire() -> ManualWire:
    start = PinMockedParent(np.array([-2.0, 0.0, 0.0]), mn.RIGHT)
    end = PinMockedParent(np.array([2.0, 0.0, 0.0]), mn.LEFT)
    return ManualWire(start, end, [])


def _make_one_corner_wire() -> ManualWire:
    start = PinMockedParent(np.array([-3.0, 0.0, 0.0]), mn.RIGHT)
    end = PinMockedParent(np.array([3.0, 0.0, 0.0]), mn.LEFT)
    return ManualWire(start, end, [np.array([0.0, 0.0, 0.0])])


def _make_two_corner_wire() -> ManualWire:
    start = PinMockedParent(np.array([-3.0, 0.0, 0.0]), mn.RIGHT)
    end = PinMockedParent(np.array([3.0, 0.0, 0.0]), mn.LEFT)
    return ManualWire(
        start, end, [np.array([-1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])]
    )


def _call_on_split(
    wire: ManualWire, alpha: float
) -> tuple[ManualWire, ManualWire, PinMockedParent, PinMockedParent]:
    wire._start.detach_wire()
    wire._end.detach_wire()
    first_end = PinMockedParent(np.array([0.0, 2.0, 0.0]), mn.DOWN)
    second_start = PinMockedParent(np.array([0.0, -2.0, 0.0]), mn.UP)
    start_portion, end_portion = wire.on_split(first_end, second_start, alpha)
    return start_portion, end_portion, first_end, second_start


# pin assignment ----------------------------------------------------------------------


def test_on_split_start_portion_retains_original_start_pin() -> None:
    wire = _make_no_corner_wire()
    original_start = wire._start

    start_portion, _end_portion, _first_end, _second_start = _call_on_split(wire, 0.5)

    assert start_portion._start is original_start


def test_on_split_start_portion_end_pin_is_first_end() -> None:
    wire = _make_no_corner_wire()

    start_portion, _end_portion, first_end, _second_start = _call_on_split(wire, 0.5)

    assert start_portion._end is first_end


def test_on_split_end_portion_start_pin_is_second_start() -> None:
    wire = _make_no_corner_wire()

    _start_portion, end_portion, _first_end, second_start = _call_on_split(wire, 0.5)

    assert end_portion._start is second_start


def test_on_split_end_portion_retains_original_end_pin() -> None:
    wire = _make_no_corner_wire()
    original_end = wire._end

    _start_portion, end_portion, _first_end, _second_start = _call_on_split(wire, 0.5)

    assert end_portion._end is original_end


# updaters -----------------------------------------------------------------------------


def test_on_split_returned_wires_have_no_updaters() -> None:
    start = PinMockedParent(np.array([-2.0, 0.0, 0.0]), mn.RIGHT)
    end = PinMockedParent(np.array([2.0, 0.0, 0.0]), mn.LEFT)
    wire = ManualWire(start, end, [], updating=True)

    start_portion, end_portion, _first_end, _second_start = _call_on_split(wire, 0.5)

    assert len(start_portion.updaters) == 0
    assert len(end_portion.updaters) == 0


# corner distribution ------------------------------------------------------------------


def test_on_split_no_corner_wire_both_halves_have_no_corners() -> None:
    wire = _make_no_corner_wire()

    start_portion, end_portion, _first_end, _second_start = _call_on_split(wire, 0.5)

    assert start_portion.get_corner_points() == []
    assert end_portion.get_corner_points() == []


def test_on_split_one_corner_wire_before_corner_start_half_empty() -> None:
    wire = _make_one_corner_wire()

    start_portion, _end_portion, _first_end, _second_start = _call_on_split(wire, 0.25)

    assert start_portion.get_corner_points() == []


def test_on_split_one_corner_wire_before_corner_end_half_has_corner() -> None:
    wire = _make_one_corner_wire()

    _start_portion, end_portion, _first_end, _second_start = _call_on_split(wire, 0.25)

    assert np.allclose(end_portion.get_corner_points(), [np.array([0.0, 0.0, 0.0])])


def test_on_split_one_corner_wire_after_corner_start_half_has_corner() -> None:
    wire = _make_one_corner_wire()

    start_portion, _end_portion, _first_end, _second_start = _call_on_split(wire, 0.75)

    assert np.allclose(start_portion.get_corner_points(), [np.array([0.0, 0.0, 0.0])])


def test_on_split_one_corner_wire_after_corner_end_half_empty() -> None:
    wire = _make_one_corner_wire()

    _start_portion, end_portion, _first_end, _second_start = _call_on_split(wire, 0.75)

    assert end_portion.get_corner_points() == []


def test_on_split_two_corner_wire_before_first_corner_start_half_empty() -> None:
    wire = _make_two_corner_wire()

    start_portion, _end_portion, _first_end, _second_start = _call_on_split(wire, 1 / 6)

    assert start_portion.get_corner_points() == []


def test_on_split_two_corner_wire_before_first_corner_end_has_both_corners() -> None:
    wire = _make_two_corner_wire()

    _start_portion, end_portion, _first_end, _second_start = _call_on_split(wire, 1 / 6)

    assert np.allclose(
        end_portion.get_corner_points(),
        [np.array([-1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])],
    )


def test_on_split_two_corner_wire_between_corners_start_half_has_first_corner() -> None:
    wire = _make_two_corner_wire()

    start_portion, _end_portion, _first_end, _second_start = _call_on_split(wire, 0.5)

    assert np.allclose(start_portion.get_corner_points(), [np.array([-1.0, 0.0, 0.0])])


def test_on_split_two_corner_wire_between_corners_end_half_has_second_corner() -> None:
    wire = _make_two_corner_wire()

    _start_portion, end_portion, _first_end, _second_start = _call_on_split(wire, 0.5)

    assert np.allclose(end_portion.get_corner_points(), [np.array([1.0, 0.0, 0.0])])


def test_on_split_two_corner_wire_after_last_corner_start_has_both_corners() -> None:
    wire = _make_two_corner_wire()

    start_portion, _end_portion, _first_end, _second_start = _call_on_split(wire, 5 / 6)

    assert np.allclose(
        start_portion.get_corner_points(),
        [np.array([-1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])],
    )


def test_on_split_two_corner_wire_after_last_corner_end_half_empty() -> None:
    wire = _make_two_corner_wire()

    _start_portion, end_portion, _first_end, _second_start = _call_on_split(wire, 5 / 6)

    assert end_portion.get_corner_points() == []


# split exactly at a corner ------------------------------------------------------------


def test_on_split_split_exactly_at_corner_neither_half_retains_it() -> None:
    wire = _make_one_corner_wire()

    start_portion, end_portion, _first_end, _second_start = _call_on_split(wire, 0.5)

    assert start_portion.get_corner_points() == []
    assert end_portion.get_corner_points() == []


# near-boundary alpha values -----------------------------------------------------------


def test_on_split_no_corner_wire_alpha_near_start_both_halves_have_no_corners() -> None:
    wire = _make_no_corner_wire()

    start_portion, end_portion, _first_end, _second_start = _call_on_split(wire, 0.01)

    assert start_portion.get_corner_points() == []
    assert end_portion.get_corner_points() == []


def test_on_split_no_corner_wire_alpha_near_end_both_halves_have_no_corners() -> None:
    wire = _make_no_corner_wire()

    start_portion, end_portion, _first_end, _second_start = _call_on_split(wire, 0.99)

    assert start_portion.get_corner_points() == []
    assert end_portion.get_corner_points() == []
