import manim as mn
import manim.typing as mnt
import numpy as np
import pytest
from utils.pin_mocked import PinMockedParent

from manim_eng import ManualWire


def _wire_from_vertices(vertices: list[mnt.Point3D]) -> ManualWire:
    """Create a ManualWire whose ``get_all_vertices()`` equals ``vertices``.

    The first and last entries in ``vertices`` become ``start.base`` and
    ``end.base`` respectively. Everything in between becomes the list of
    explicit corner points passed to ``ManualWire``.
    """
    start = PinMockedParent(vertices[0], mn.RIGHT)
    end = PinMockedParent(vertices[-1], mn.RIGHT)
    corners = vertices[1:-1]
    return ManualWire(start, end, corners)


# --------------------------------------------------------------------------------------
# get_point_closest_to
# --------------------------------------------------------------------------------------


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

# Shorter L-shaped wire.
L_WIRE_VERTICES_B: list[mnt.Point3D] = [
    np.array([0.0, 0.0, 0.0]),
    np.array([1.0, 0.0, 0.0]),
    np.array([1.0, 1.0, 0.0]),
]


def test_get_closest_point_to_projects_onto_interior() -> None:
    # Point at (0, 1, 0) projects perpendicularly onto the midpoint of the segment.
    wire = _wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    point = np.array([0.0, 1.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([0.0, 0.0, 0.0])


def test_get_closest_point_to_clamps_to_start() -> None:
    # Point before the start of the segment — clamps to start.
    # Point before the start of the segment — clamps to start.
    wire = _wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    point = np.array([-3.0, 1.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([-1.0, 0.0, 0.0])


def test_get_closest_point_to_clamps_to_end() -> None:
    # Point past the end of the segment — clamps to end.
    wire = _wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    point = np.array([3.0, 1.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([1.0, 0.0, 0.0])


def test_get_closest_point_to_pin_on_segment() -> None:
    # Point lies exactly on the segment
    wire = _wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    point = np.array([0.0, 0.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([0.0, 0.0, 0.0])


def test_get_closest_point_to_pin_at_start_vertex() -> None:
    # Point coincides with the start vertex.
    wire = _wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    point = np.array([-1.0, 0.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([-1.0, 0.0, 0.0])


def test_get_closest_point_to_degenerate_segment() -> None:
    # Wire is a degenerate zero-length segment; both vertices at (0, 0, 0).
    # Two distinct points at the same position satisfy start != end.
    degenerate_wire = _wire_from_vertices(
        [
            np.array([0.0, 0.0, 0.0]),
            np.array([0.0, 0.0, 0.0]),
        ]
    )
    point = np.array([3.0, 4.0, 0.0])

    closest = degenerate_wire.get_point_closest_to(point)

    assert closest == pytest.approx([0.0, 0.0, 0.0])


def test_get_closest_point_to_multi_segment_second_wins() -> None:
    # L-shaped wire; the point is on the second (vertical) segment.
    wire = _wire_from_vertices(L_WIRE_VERTICES_A)
    point = np.array([2.0, 1.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([2.0, 1.0, 0.0])


def test_get_closest_point_to_pin_at_corner_vertex() -> None:
    # Point coincides with the corner vertex shared by both segments.
    wire = _wire_from_vertices(L_WIRE_VERTICES_B)
    point = np.array([1.0, 0.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([1.0, 0.0, 0.0])


def test_get_closest_point_to_equidistant_from_two_segments() -> None:
    # Point equidistant from both segments; the earlier segment takes priority.
    wire = _wire_from_vertices(L_WIRE_VERTICES_B)
    point = np.array([0.5, 0.5, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([0.5, 0.0, 0.0])


def test_get_closest_point_to_accepts_pin() -> None:
    # Passing a Pin should give the same result as passing pin.tip directly.
    wire = _wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    pin = PinMockedParent(np.array([0.0, 1.0, 0.0]), mn.RIGHT)

    closest_via_pin = wire.get_point_closest_to(pin)
    closest_via_tip = wire.get_point_closest_to(pin.tip)

    assert closest_via_pin == pytest.approx(closest_via_tip)


# --------------------------------------------------------------------------------------
# get_closest_points_with
# --------------------------------------------------------------------------------------


def test_get_closest_points_with_crossing_wires() -> None:
    # Two perpendicular wires that cross; closest points are both at the intersection.
    first = _wire_from_vertices([np.array([-1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])])
    second = _wire_from_vertices(
        [np.array([0.0, -1.0, 0.0]), np.array([0.0, 1.0, 0.0])]
    )

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([0.0, 0.0, 0.0])
    assert q == pytest.approx([0.0, 0.0, 0.0])


def test_get_closest_points_with_parallel_overlapping() -> None:
    # Parallel wires at different y-offsets with overlapping x-ranges.
    first = _wire_from_vertices([np.array([0.0, 0.0, 0.0]), np.array([2.0, 0.0, 0.0])])
    second = _wire_from_vertices([np.array([1.0, 1.0, 0.0]), np.array([3.0, 1.0, 0.0])])

    p, _q = first.get_closest_points_with(second)

    # Overlap is [1, 2] on the first wire's axis; midpoint is (1.5, 0, 0).
    assert p == pytest.approx([1.5, 0.0, 0.0])


def test_get_closest_points_with_parallel_non_overlapping() -> None:
    # Parallel wires with a gap between them; closest points are the facing endpoints.
    first = _wire_from_vertices([np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])])
    second = _wire_from_vertices([np.array([3.0, 0.0, 0.0]), np.array([4.0, 0.0, 0.0])])

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([1.0, 0.0, 0.0])
    assert q == pytest.approx([3.0, 0.0, 0.0])


def test_get_closest_points_with_multi_segment_global_minimum_selected() -> None:
    # L-shaped first wire vs horizontal second wire; the closest pair is on the
    # vertical segment of the first wire, not the horizontal one.
    first = _wire_from_vertices(
        [
            np.array([0.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            np.array([1.0, 1.0, 0.0]),
        ]
    )
    second = _wire_from_vertices([np.array([0.0, 0.5, 0.0]), np.array([2.0, 0.5, 0.0])])

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([1.0, 0.5, 0.0])
    assert q == pytest.approx([1.0, 0.5, 0.0])


def test_get_closest_points_with_closest_pair_on_second_segments() -> None:
    # Regression: the outer loop must iterate self, not other. This test places the
    # closest pair on the second segment of both wires, which would return wrong results
    # if self.get_all_vertices() were replaced by other.get_all_vertices() in the outer
    # loop.
    first = _wire_from_vertices(
        [
            np.array([0.0, 0.0, 0.0]),
            np.array([0.0, 2.0, 0.0]),
            np.array([0.0, 4.0, 0.0]),
        ]
    )
    second = _wire_from_vertices(
        [
            np.array([5.0, 0.0, 0.0]),
            np.array([5.0, 2.0, 0.0]),
            np.array([1.0, 2.0, 0.0]),
        ]
    )

    p, q = first.get_closest_points_with(second)

    # The second segment of each wire is closest; they meet at (0, 2, 0) and (1, 2, 0).
    assert p == pytest.approx([0.0, 2.0, 0.0])
    assert q == pytest.approx([1.0, 2.0, 0.0])


def test_get_closest_points_with_return_order() -> None:
    # First element of the tuple must be on self, second on other.
    first = _wire_from_vertices([np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])])
    second = _wire_from_vertices([np.array([0.0, 2.0, 0.0]), np.array([1.0, 2.0, 0.0])])

    p, q = first.get_closest_points_with(second)

    # p must lie on first (y == 0), q must lie on second (y == 2).
    assert p[1] == pytest.approx(0.0)
    assert q[1] == pytest.approx(2.0)
