import manim.typing as mnt
import numpy as np
import pytest
from utils.wire_from_vertices import manual_wire_from_vertices

# A single horizontal segment from (-1,0,0) to (1,0,0).
HORIZONTAL_WIRE_VERTICES: list[mnt.Point3D] = [
    np.array([-1.0, 0.0, 0.0]),
    np.array([1.0, 0.0, 0.0]),
]

# L-shaped wire (horizontal then vertical).
L_WIRE_VERTICES_A: list[mnt.Point3D] = [
    np.array([0.0, 0.0, 0.0]),
    np.array([2.0, 0.0, 0.0]),
    np.array([2.0, 2.0, 0.0]),
]

# Three-segment wire: (0,0,0)->(2,0,0)->(2,2,0)->(0,2,0), total length 6.
THREE_SEGMENT_WIRE_VERTICES: list[mnt.Point3D] = [
    np.array([0.0, 0.0, 0.0]),
    np.array([2.0, 0.0, 0.0]),
    np.array([2.0, 2.0, 0.0]),
    np.array([0.0, 2.0, 0.0]),
]


# --------------------------------------------------------------------------------------
# get_alpha_at_point
# --------------------------------------------------------------------------------------


# Straight wire (HORIZONTAL_WIRE_VERTICES: (-1,0,0)->(1,0,0), total length 2) ----------


def test_get_alpha_at_point_returns_zero_at_start_base() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([-1.0, 0.0, 0.0]))

    assert result == pytest.approx(0.0)


def test_get_alpha_at_point_returns_one_at_end_base() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([1.0, 0.0, 0.0]))

    assert result == pytest.approx(1.0)


def test_get_alpha_at_point_returns_half_at_midpoint() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([0.0, 0.0, 0.0]))

    assert result == pytest.approx(0.5)


def test_get_alpha_at_point_returns_quarter_at_one_quarter_point() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([-0.5, 0.0, 0.0]))

    assert result == pytest.approx(0.25)


def test_get_alpha_at_point_returns_three_quarters_at_three_quarter_point() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([0.5, 0.0, 0.0]))

    assert result == pytest.approx(0.75)


def test_get_alpha_at_point_return_value_is_float() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([0.0, 0.0, 0.0]))

    assert isinstance(result, float)


# L-shaped wire (L_WIRE_VERTICES_A: (0,0,0)->(2,0,0)->(2,2,0), total length 4) ---------


def test_get_alpha_at_point_returns_zero_at_start_on_l_wire() -> None:
    wire = manual_wire_from_vertices(L_WIRE_VERTICES_A)

    result = wire.get_alpha_at_point(np.array([0.0, 0.0, 0.0]))

    assert result == pytest.approx(0.0)


def test_get_alpha_at_point_returns_half_at_corner() -> None:
    wire = manual_wire_from_vertices(L_WIRE_VERTICES_A)

    result = wire.get_alpha_at_point(np.array([2.0, 0.0, 0.0]))

    assert result == pytest.approx(0.5)


def test_get_alpha_at_point_returns_one_at_end_on_l_wire() -> None:
    wire = manual_wire_from_vertices(L_WIRE_VERTICES_A)

    result = wire.get_alpha_at_point(np.array([2.0, 2.0, 0.0]))

    assert result == pytest.approx(1.0)


def test_get_alpha_at_point_returns_correct_alpha_on_first_segment() -> None:
    wire = manual_wire_from_vertices(L_WIRE_VERTICES_A)

    result = wire.get_alpha_at_point(np.array([1.0, 0.0, 0.0]))

    assert result == pytest.approx(0.25)


def test_get_alpha_at_point_returns_correct_alpha_on_second_segment() -> None:
    wire = manual_wire_from_vertices(L_WIRE_VERTICES_A)

    result = wire.get_alpha_at_point(np.array([2.0, 1.0, 0.0]))

    assert result == pytest.approx(0.75)


# Three-segment wire ((0,0,0)->(2,0,0)->(2,2,0)->(0,2,0), total length 6) --------------


def test_get_alpha_at_point_on_third_segment_of_three_segment_wire() -> None:
    wire = manual_wire_from_vertices(THREE_SEGMENT_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([1.0, 2.0, 0.0]))

    assert result == pytest.approx(5 / 6)


def test_get_alpha_at_point_at_second_corner_of_three_segment_wire() -> None:
    wire = manual_wire_from_vertices(THREE_SEGMENT_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([2.0, 2.0, 0.0]))

    assert result == pytest.approx(4 / 6)


# Off-wire points ----------------------------------------------------------------------


def test_get_alpha_at_point_returns_none_for_point_off_perpendicular() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([0.0, 1.0, 0.0]))

    assert result is None


def test_get_alpha_at_point_returns_none_for_point_before_start() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([-3.0, 0.0, 0.0]))

    assert result is None


def test_get_alpha_at_point_returns_none_for_point_after_end() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([3.0, 0.0, 0.0]))

    assert result is None


def test_get_alpha_at_point_returns_none_for_completely_unrelated_point() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([10.0, 10.0, 0.0]))

    assert result is None


def test_get_alpha_at_point_returns_none_for_point_off_l_wire_in_gap() -> None:
    wire = manual_wire_from_vertices(L_WIRE_VERTICES_A)

    result = wire.get_alpha_at_point(np.array([1.0, 1.0, 0.0]))

    assert result is None


# Boundary cases -----------------------------------------------------------------------


def test_get_alpha_at_point_very_close_to_start_returns_near_zero() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([-1.0 + 1e-6, 0.0, 0.0]))

    assert result is not None
    assert result == pytest.approx(0.0, abs=1e-5)


def test_get_alpha_at_point_very_close_to_end_returns_near_one() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    result = wire.get_alpha_at_point(np.array([1.0 - 1e-6, 0.0, 0.0]))

    assert result is not None
    assert result == pytest.approx(1.0, abs=1e-5)


def test_get_alpha_at_point_at_corner_vertex_is_not_none() -> None:
    wire = manual_wire_from_vertices(L_WIRE_VERTICES_A)

    result = wire.get_alpha_at_point(np.array([2.0, 0.0, 0.0]))

    assert result is not None


# Round-trip consistency ---------------------------------------------------------------


def test_get_alpha_at_point_returned_alpha_within_zero_and_one() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    points = [
        np.array([-1.0, 0.0, 0.0]),
        np.array([-0.5, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0]),
        np.array([0.5, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
    ]

    for point in points:
        result = wire.get_alpha_at_point(point)
        assert result is not None
        assert 0.0 <= result <= 1.0


def test_get_alpha_at_point_is_consistent_with_point_from_proportion() -> None:
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)

    for alpha in [0.0, 0.25, 0.5, 0.75, 1.0]:
        point = wire.point_from_proportion(alpha)
        result = wire.get_alpha_at_point(point)
        assert result == pytest.approx(alpha)


# Orientations -------------------------------------------------------------------------


def test_get_alpha_at_point_works_on_vertical_wire() -> None:
    wire = manual_wire_from_vertices(
        [np.array([0.0, -1.0, 0.0]), np.array([0.0, 1.0, 0.0])]
    )

    result = wire.get_alpha_at_point(np.array([0.0, 0.0, 0.0]))

    assert result == pytest.approx(0.5)


def test_get_alpha_at_point_works_on_diagonal_wire() -> None:
    wire = manual_wire_from_vertices(
        [np.array([0.0, 0.0, 0.0]), np.array([1.0, 1.0, 0.0])]
    )

    result = wire.get_alpha_at_point(np.array([0.5, 0.5, 0.0]))

    assert result == pytest.approx(0.5)
