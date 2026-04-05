from typing import Callable

import manim as mn
import numpy as np
import pytest
from utils.pin_mocked import PinMockedParent

from manim_eng import Wire
from manim_eng._utils.utils import cardinalised

# --------------------------------------------------------------------------------------
# get_corner_points
# --------------------------------------------------------------------------------------

# tip insertion (cardinal vs non-cardinal pins) ----------------------------------------


def test_get_corner_points_cardinal_start_does_not_include_start_tip(
    wire_with_one_corner: Wire,
) -> None:
    # wire_with_one_corner: start=Pin(ORIGIN, RIGHT), end=Pin(RIGHT+UP, UP)
    # Both cardinal, perpendicular → single routing corner, no tip insertion.
    start = wire_with_one_corner._start
    end = wire_with_one_corner._end

    result = wire_with_one_corner.get_corner_points()

    assert len(result) == 1
    assert not any(np.allclose(p, start.tip) for p in result)
    assert not any(np.allclose(p, end.tip) for p in result)


def test_get_corner_points_non_cardinal_start_inserts_start_tip_as_first_corner() -> (
    None
):
    # Diagonal start direction [1,1,0] with end placed far enough that the intersection
    # of the two rays is beyond start.length, so the early-return is not taken and the
    # tip-insertion branch prepends start.tip.
    start = PinMockedParent(mn.ORIGIN, np.array([1.0, 1.0, 0.0]))
    end = PinMockedParent(np.array([3.0, 0.0, 0.0]), mn.UP)
    wire = Wire(start, end)

    result = wire.get_corner_points()

    assert len(result) == 2  # noqa: PLR2004
    assert np.allclose(result[0], start.tip)


def test_get_corner_points_non_cardinal_end_inserts_end_tip_as_last_corner() -> None:
    # Cardinal start, mostly-DOWN (non-cardinal) end. The routing helper produces one
    # corner; then end.tip is appended because end is non-cardinal.
    start = PinMockedParent(mn.ORIGIN, mn.RIGHT)
    end = PinMockedParent(np.array([3.0, 3.0, 0.0]), np.array([0.1, -1.0, 0.0]))
    wire = Wire(start, end)

    result = wire.get_corner_points()

    assert len(result) == 2  # noqa: PLR2004
    assert np.allclose(result[-1], end.tip)


def test_get_corner_points_both_non_cardinal_pins_inserts_both_tips() -> None:
    # Both pins diagonal. Routing helper produces one corner; both tips are inserted
    # around it.
    start = PinMockedParent(mn.ORIGIN, np.array([1.0, 1.0, 0.0]))
    end = PinMockedParent(np.array([4.0, 4.0, 0.0]), np.array([0.1, -1.0, 0.0]))
    wire = Wire(start, end)

    result = wire.get_corner_points()

    assert len(result) == 3  # noqa: PLR2004
    assert np.allclose(result[0], start.tip)
    assert np.allclose(result[-1], end.tip)


def test_get_corner_points_cardinal_pins_return_value_does_not_contain_either_tip(
    wire_with_one_corner: Wire,
) -> None:
    # Explicit negative: neither tip coordinate should appear in the result when both
    # pins are cardinal.
    start = wire_with_one_corner._start
    end = wire_with_one_corner._end

    result = wire_with_one_corner.get_corner_points()

    assert not any(np.allclose(p, start.tip) for p in result)
    assert not any(np.allclose(p, end.tip) for p in result)


# intersection-override (early-return) logic -------------------------------------------


def test_get_corner_points_perpendicular_facing_pins_returns_intersection() -> None:
    # Two cardinal pins whose extended rays cross at a single point in front of both.
    # Branch: intersection_in_front=True, cardinal_or_intersection_in_pin=True → early
    # return fires, yielding the raw intersection as the sole corner.
    start = PinMockedParent(np.array([0.0, 1.0, 0.0]), mn.RIGHT)
    end = PinMockedParent(np.array([1.0, 0.0, 0.0]), mn.UP)
    wire = Wire(start, end)

    result = wire.get_corner_points()

    assert len(result) == 1
    assert np.allclose(result[0], np.array([1.0, 1.0, 0.0]))


def test_get_corner_points_intersection_behind_end_bypasses_early_return() -> None:
    # start points RIGHT from ORIGIN; end points DOWN from (1, -1, 0).
    # The lines cross at (1, 0, 0) but that point is behind end's pin (end_proj < 0),
    # so the early return is bypassed and the routing helper is invoked instead.
    # The routing helper places the corner via the pin tips, which produces a different
    # point from the raw intersection — confirming the early-return path was NOT taken.
    start = PinMockedParent(mn.ORIGIN, mn.RIGHT)
    end = PinMockedParent(np.array([1.0, -1.0, 0.0]), mn.DOWN)
    raw_intersection = mn.find_intersection(
        [start.base], [start.direction], [end.base], [end.direction]
    )[0]
    wire = Wire(start, end)

    result = wire.get_corner_points()

    assert len(result) == 1
    assert not np.allclose(result[0], raw_intersection)


def test_get_corner_points_non_cardinal_near_intersection_takes_early_return() -> None:
    # Non-cardinal start pin with the ray intersection landing within start.length of
    # start.base (start_proj <= start.length). The early return fires: result has one
    # element and it is NOT start.tip — the tip-insertion code is never reached.
    start = PinMockedParent(mn.ORIGIN, np.array([1.0, 1.0, 0.0]))
    # end placed so the intersection of the two rays is at (0.1, 0.1, 0), well within
    # start.length ≈ 0.4.
    end = PinMockedParent(np.array([0.1, 2.0, 0.0]), mn.DOWN)
    wire = Wire(start, end)

    result = wire.get_corner_points()

    assert len(result) == 1
    assert not np.allclose(result[0], start.tip)


def test_get_corner_points_non_cardinal_far_intersection_inserts_tip() -> None:
    # Non-cardinal start pin; end is far enough that the intersection of the two rays
    # falls well beyond start.length.  Early return is NOT taken; tip-insertion fires
    # and start.tip becomes the first corner.
    start = PinMockedParent(mn.ORIGIN, np.array([1.0, 1.0, 0.0]))
    end = PinMockedParent(np.array([2.0, 4.0, 0.0]), mn.DOWN)
    wire = Wire(start, end)

    result = wire.get_corner_points()

    assert len(result) == 2  # noqa: PLR2004
    assert np.allclose(result[0], start.tip)


def test_get_corner_points_collinear_opposing_overlapping_pins_early_return() -> None:
    # Two collinear, anti-parallel cardinal pins whose tips overlap (bases are closer
    # than start.length + end.length ≈ 0.8).
    # mn.find_intersection returns start.base; parallel_but_pins_intersecting=True so
    # the early-return fires.
    start = PinMockedParent(mn.ORIGIN, mn.RIGHT)  # base = (0 ,0, 0), tip = (0.4, 0, 0)
    end = PinMockedParent(
        np.array([0.6, 0.0, 0.0]), mn.LEFT
    )  # base = (0.6, 0, 0), tip = (0.2, 0, 0)
    wire = Wire(start, end)

    result = wire.get_corner_points()

    assert len(result) == 0


def test_get_corner_points_parallel_same_direction_pins_skips_early_return() -> None:
    # Two cardinal pins pointing in the same direction but offset vertically.
    # The parallel_but_pins_intersecting guard is False; the early-return for facing
    # pins also doesn't fire. The parallel helper is invoked and returns 2 routing
    # corners.
    start = PinMockedParent(mn.LEFT * 2, mn.RIGHT)
    end = PinMockedParent(mn.RIGHT * 2 + mn.UP, mn.RIGHT)
    wire = Wire(start, end)

    result = wire.get_corner_points()

    assert len(result) == 2  # noqa: PLR2004


# additional edges ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "make_wire",
    [
        # perpendicular cardinal
        lambda: Wire(
            PinMockedParent(mn.ORIGIN, mn.RIGHT),
            PinMockedParent(mn.RIGHT + mn.UP, mn.UP),
        ),
        # parallel same-direction
        lambda: Wire(
            PinMockedParent(mn.LEFT * 2, mn.RIGHT),
            PinMockedParent(mn.RIGHT * 2 + mn.UP, mn.RIGHT),
        ),
        # perpendicular with intersection in front of both (early-return branch)
        lambda: Wire(
            PinMockedParent(np.array([0.0, 1.0, 0.0]), mn.RIGHT),
            PinMockedParent(np.array([1.0, 0.0, 0.0]), mn.UP),
        ),
        # non-cardinal start, cardinal end
        lambda: Wire(
            PinMockedParent(mn.ORIGIN, np.array([1.0, 1.0, 0.0])),
            PinMockedParent(np.array([3.0, 0.0, 0.0]), mn.UP),
        ),
    ],
    ids=[
        "perpendicular_cardinal",
        "parallel_same_direction",
        "perpendicular_facing",
        "non_cardinal_start",
    ],
)
def test_get_corner_points_never_includes_start_base_or_end_base(
    make_wire: Callable[[], Wire],
) -> None:
    wire = make_wire()
    start_base = wire._start.base
    end_base = wire._end.base

    result = wire.get_corner_points()

    assert not any(np.allclose(p, start_base) for p in result)
    assert not any(np.allclose(p, end_base) for p in result)


def test_get_corner_points_perpendicular_cardinal_pins_returns_exactly_one_corner(
    wire_with_one_corner: Wire,
) -> None:
    result = wire_with_one_corner.get_corner_points()

    assert len(result) == 1


def test_get_corner_points_parallel_same_direction_pins_returns_exactly_two_corners(
    wire_with_two_corners: Wire,
) -> None:
    result = wire_with_two_corners.get_corner_points()

    assert len(result) == 2  # noqa: PLR2004


def test_get_corner_points_corners_are_axis_aligned_with_pin_tips(
    wire_with_one_corner: Wire,
) -> None:
    # For perpendicular cardinal pins the routing helper places its single corner at the
    # intersection of the two lines extending from the pin tips. That point must share
    # either the x-coordinate of one tip or the y-coordinate of one tip (it lies on the
    # orthogonal routing grid defined by the tips).
    start = wire_with_one_corner._start
    end = wire_with_one_corner._end

    result = wire_with_one_corner.get_corner_points()

    for corner in result:
        on_start_x = np.isclose(corner[0], start.tip[0])
        on_start_y = np.isclose(corner[1], start.tip[1])
        on_end_x = np.isclose(corner[0], end.tip[0])
        on_end_y = np.isclose(corner[1], end.tip[1])
        assert on_start_x or on_start_y or on_end_x or on_end_y


def test_get_corner_points_is_deterministic(wire_with_one_corner: Wire) -> None:
    first = wire_with_one_corner.get_corner_points()
    second = wire_with_one_corner.get_corner_points()

    assert len(first) == len(second)
    for a, b in zip(first, second, strict=True):
        assert np.allclose(a, b)


def test_get_corner_points_perpendicular_corner_is_in_front_of_both_pin_tips(
    wire_with_one_corner: Wire,
) -> None:
    # The routing corner must not lie behind either pin's face (i.e. the dot product of
    # (corner - tip) with the cardinalised pin direction must be non-negative).
    start = wire_with_one_corner._start
    end = wire_with_one_corner._end

    result = wire_with_one_corner.get_corner_points()

    assert len(result) == 1
    corner = result[0]
    assert np.dot(corner - start.tip, cardinalised(start.direction)) >= 0
    assert np.dot(corner - end.tip, cardinalised(end.direction)) >= 0
