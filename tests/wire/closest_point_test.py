import manim as mn
import manim.typing as mnt
import numpy as np
import pytest
from utils.pin_mocked import PinMockedParent
from utils.wire_from_vertices import manual_wire_from_vertices

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
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    point = np.array([0.0, 1.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([0.0, 0.0, 0.0])


def test_get_closest_point_to_clamps_to_start() -> None:
    # Point before the start of the segment — clamps to start.
    # Point before the start of the segment — clamps to start.
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    point = np.array([-3.0, 1.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([-1.0, 0.0, 0.0])


def test_get_closest_point_to_clamps_to_end() -> None:
    # Point past the end of the segment — clamps to end.
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    point = np.array([3.0, 1.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([1.0, 0.0, 0.0])


def test_get_closest_point_to_pin_on_segment() -> None:
    # Point lies exactly on the segment
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    point = np.array([0.0, 0.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([0.0, 0.0, 0.0])


def test_get_closest_point_to_pin_at_start_vertex() -> None:
    # Point coincides with the start vertex.
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    point = np.array([-1.0, 0.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([-1.0, 0.0, 0.0])


def test_get_closest_point_to_degenerate_segment() -> None:
    # Wire is a degenerate zero-length segment; both vertices at (0, 0, 0).
    # Two distinct points at the same position satisfy start != end.
    degenerate_wire = manual_wire_from_vertices(
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
    wire = manual_wire_from_vertices(L_WIRE_VERTICES_A)
    point = np.array([2.0, 1.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([2.0, 1.0, 0.0])


def test_get_closest_point_to_pin_at_corner_vertex() -> None:
    # Point coincides with the corner vertex shared by both segments.
    wire = manual_wire_from_vertices(L_WIRE_VERTICES_B)
    point = np.array([1.0, 0.0, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([1.0, 0.0, 0.0])


def test_get_closest_point_to_equidistant_from_two_segments() -> None:
    # Point equidistant from both segments; the earlier segment takes priority.
    wire = manual_wire_from_vertices(L_WIRE_VERTICES_B)
    point = np.array([0.5, 0.5, 0.0])

    closest = wire.get_point_closest_to(point)

    assert closest == pytest.approx([0.5, 0.0, 0.0])


def test_get_closest_point_to_accepts_pin_and_takes_tip() -> None:
    # Passing a Pin should give the same result as passing pin.tip directly.
    wire = manual_wire_from_vertices(HORIZONTAL_WIRE_VERTICES)
    pin = PinMockedParent(np.array([0.0, 1.0, 0.0]), mn.RIGHT)

    closest_via_pin = wire.get_point_closest_to(pin)
    closest_via_tip = wire.get_point_closest_to(pin.tip)

    assert closest_via_pin == pytest.approx(closest_via_tip)


# --------------------------------------------------------------------------------------
# get_closest_points_with
# --------------------------------------------------------------------------------------


def test_get_closest_points_with_crossing_wires() -> None:
    # Two perpendicular wires that cross; closest points are both at the intersection.
    first = manual_wire_from_vertices(
        [np.array([-1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])]
    )
    second = manual_wire_from_vertices(
        [np.array([0.0, -1.0, 0.0]), np.array([0.0, 1.0, 0.0])]
    )

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([0.0, 0.0, 0.0])
    assert q == pytest.approx([0.0, 0.0, 0.0])


def test_get_closest_points_with_parallel_overlapping() -> None:
    # Parallel wires at different y-offsets with overlapping x-ranges.
    first = manual_wire_from_vertices(
        [np.array([0.0, 0.0, 0.0]), np.array([2.0, 0.0, 0.0])]
    )
    second = manual_wire_from_vertices(
        [np.array([1.0, 1.0, 0.0]), np.array([3.0, 1.0, 0.0])]
    )

    p, _q = first.get_closest_points_with(second)

    # Overlap is [1, 2] on the first wire's axis; midpoint is (1.5, 0, 0).
    assert p == pytest.approx([1.5, 0.0, 0.0])


def test_get_closest_points_with_parallel_non_overlapping() -> None:
    # Parallel wires with a gap between them; closest points are the facing endpoints.
    first = manual_wire_from_vertices(
        [np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])]
    )
    second = manual_wire_from_vertices(
        [np.array([3.0, 0.0, 0.0]), np.array([4.0, 0.0, 0.0])]
    )

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([1.0, 0.0, 0.0])
    assert q == pytest.approx([3.0, 0.0, 0.0])


def test_get_closest_points_with_multi_segment_global_minimum_selected() -> None:
    # L-shaped first wire vs horizontal second wire; the closest pair is on the
    # vertical segment of the first wire, not the horizontal one.
    first = manual_wire_from_vertices(
        [
            np.array([0.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            np.array([1.0, 1.0, 0.0]),
        ]
    )
    second = manual_wire_from_vertices(
        [np.array([0.0, 0.5, 0.0]), np.array([2.0, 0.5, 0.0])]
    )

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([1.0, 0.5, 0.0])
    assert q == pytest.approx([1.0, 0.5, 0.0])


def test_get_closest_points_with_closest_pair_on_second_segments() -> None:
    # Regression: the outer loop must iterate self, not other. This test places the
    # closest pair on the second segment of both wires, which would return wrong results
    # if self.get_all_vertices() were replaced by other.get_all_vertices() in the outer
    # loop.
    first = manual_wire_from_vertices(
        [
            np.array([0.0, 0.0, 0.0]),
            np.array([0.0, 2.0, 0.0]),
            np.array([0.0, 4.0, 0.0]),
        ]
    )
    second = manual_wire_from_vertices(
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
    first = manual_wire_from_vertices(
        [np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])]
    )
    second = manual_wire_from_vertices(
        [np.array([0.0, 2.0, 0.0]), np.array([1.0, 2.0, 0.0])]
    )

    p, q = first.get_closest_points_with(second)

    # p must lie on first (y == 0), q must lie on second (y == 2).
    assert p[1] == pytest.approx(0.0)
    assert q[1] == pytest.approx(2.0)


# --------------------------------------------------------------------------------------
# parallel non-collinear tie-breaking
# --------------------------------------------------------------------------------------


def test_get_closest_points_with_c_shape_prefers_parallel_facing_segments() -> None:
    # Two C-shaped wires facing each other (the docstring diagram). The corners are
    # equidistant from each other, but the midpoints of the facing vertical segments
    # are the 'logical' closest points and should be preferred by the tie-break.
    #
    # first:  (-2,1)→(-1,1)→(-1,-1)→(-2,-1)   (C opening right)
    # second: ( 2,1)→( 1,1)→( 1,-1)→( 2,-1)   (C opening left)
    #
    # (first.seg0, second.seg0): collinear horizontals at y=1. Closest (-1,1) and
    # (1,1), dist²=4. Sets best.
    # (first.seg1, second.seg1): vertical x=-1 vs vertical x=1, parallel, NOT collinear.
    # Overlap y∈[-1,1]. Midpoint (-1,0) and (1,0), dist²=4. Tie + parallel → overrides.
    first = manual_wire_from_vertices(
        [
            np.array([-2.0, 1.0, 0.0]),
            np.array([-1.0, 1.0, 0.0]),
            np.array([-1.0, -1.0, 0.0]),
            np.array([-2.0, -1.0, 0.0]),
        ]
    )
    second = manual_wire_from_vertices(
        [
            np.array([2.0, 1.0, 0.0]),
            np.array([1.0, 1.0, 0.0]),
            np.array([1.0, -1.0, 0.0]),
            np.array([2.0, -1.0, 0.0]),
        ]
    )

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([-1.0, 0.0, 0.0])
    assert q == pytest.approx([1.0, 0.0, 0.0])
    # The corners must not have been returned.
    corners = [[-1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [-1.0, -1.0, 0.0], [1.0, -1.0, 0.0]]
    for corner in corners:
        assert p != pytest.approx(corner)
        assert q != pytest.approx(corner)


def test_get_closest_points_with_parallel_non_collinear_tie_overrides() -> None:
    # An earlier non-parallel pair sets best at dist²=1, then a later
    # parallel+non-collinear pair also has dist²=1 and overrides it.
    #
    # first:  (0,0)->(2,0)              (single horizontal at y=0)
    # second: (3,1)->(3,-1)->(1,-1)     (vertical at x=3, then horizontal y=-1)
    #
    # (first.seg0, second.seg0): horizontal y=0 vs vertical x=3, perpendicular.
    # Closest (2,0,0) and (3,0,0), dist²=1. Sets best.
    # (first.seg0, second.seg1): horizontal y=0 vs horizontal y=-1, parallel, NOT
    # collinear. x-overlap [1,2]; midpoint (1.5,0) and (1.5,-1), dist²=1.
    # Tie + parallel -> overrides.
    first = manual_wire_from_vertices(
        [
            np.array([0.0, 0.0, 0.0]),
            np.array([2.0, 0.0, 0.0]),
        ]
    )
    second = manual_wire_from_vertices(
        [
            np.array([3.0, 1.0, 0.0]),
            np.array([3.0, -1.0, 0.0]),
            np.array([1.0, -1.0, 0.0]),
        ]
    )

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([1.5, 0.0, 0.0])
    assert q == pytest.approx([1.5, -1.0, 0.0])


def test_get_closest_points_with_collinear_tie_does_not_override() -> None:
    # A later parallel+collinear pair at the same distance must NOT override the earlier
    # result — the `not segments_collinear` guard suppresses the override in that case.
    #
    # first:  (0,2)->(0,0)->(-2,0)    (vertical down to origin, then horizontal left)
    # second: (1,0)->(3,0)            (single horizontal at y=0)
    #
    # (first.seg0, second.seg0): vertical x=0 vs horizontal y=0, perpendicular.
    # Closest (0,0,0) and (1,0,0), dist²=1. Sets best.
    # (first.seg1, second.seg0): horizontal y=0 vs horizontal y=0, parallel AND
    # collinear. Closest (0,0,0) and (1,0,0), dist²=1. Tie, but collinear — guard
    # fires, no override.
    first = manual_wire_from_vertices(
        [
            np.array([0.0, 2.0, 0.0]),
            np.array([0.0, 0.0, 0.0]),
            np.array([-2.0, 0.0, 0.0]),
        ]
    )
    second = manual_wire_from_vertices(
        [
            np.array([1.0, 0.0, 0.0]),
            np.array([3.0, 0.0, 0.0]),
        ]
    )

    p, q = first.get_closest_points_with(second)

    # The result is stable: the collinear guard prevents the second pair from overriding
    # the first, even though both pairs yield the same closest points in this geometry.
    assert p == pytest.approx([0.0, 0.0, 0.0])
    assert q == pytest.approx([1.0, 0.0, 0.0])


def test_get_closest_points_with_strictly_closer_non_parallel_wins() -> None:
    # A strictly closer non-parallel pair wins even when a parallel+non-collinear pair
    # was encountered first — the tie-break does not promote parallel pairs when it is
    # not a true tie.
    #
    # first:  (0,0)->(2,0)->(2,2)     (horizontal, then vertical)
    # second: (1,0.5)->(3,0.5)        (single horizontal at y=0.5)
    #
    # (first.seg0, second.seg0): horizontal y=0 vs horizontal y=0.5, parallel, NOT
    # collinear. x-overlap [1,2]; midpoint (1.5,0) and (1.5,0.5), dist²=0.25. Sets best.
    # (first.seg1, second.seg0): vertical x=2 vs horizontal y=0.5, perpendicular.
    # Closest (2,0.5,0) and (2,0.5,0), dist²=0. Strictly closer — overrides via
    # `dist < best_dist`.
    first = manual_wire_from_vertices(
        [
            np.array([0.0, 0.0, 0.0]),
            np.array([2.0, 0.0, 0.0]),
            np.array([2.0, 2.0, 0.0]),
        ]
    )
    second = manual_wire_from_vertices(
        [
            np.array([1.0, 0.5, 0.0]),
            np.array([3.0, 0.5, 0.0]),
        ]
    )

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([2.0, 0.5, 0.0])
    assert q == pytest.approx([2.0, 0.5, 0.0])


def test_get_closest_points_with_c_shape_horiz_prefers_parallel_facing_segments() -> (
    None
):
    # Same as the vertical C-shape test but rotated 90°: C-shapes opening down/up.
    # Confirms the tie-breaking logic is axis-agnostic.
    #
    # first:  (-1,2)->(-1,1)->(1,1)->(1,2)      (C opening downward)
    # second: (-1,-2)->(-1,-1)->(1,-1)->(1,-2)  (C opening upward)
    #
    # The facing segments (-1,1)->(1,1) and (-1,-1)->(1,-1) are horizontal, parallel,
    # and not collinear. The corners are equidistant; the parallel tie-break selects
    # midpoints.
    first = manual_wire_from_vertices(
        [
            np.array([-1.0, 2.0, 0.0]),
            np.array([-1.0, 1.0, 0.0]),
            np.array([1.0, 1.0, 0.0]),
            np.array([1.0, 2.0, 0.0]),
        ]
    )
    second = manual_wire_from_vertices(
        [
            np.array([-1.0, -2.0, 0.0]),
            np.array([-1.0, -1.0, 0.0]),
            np.array([1.0, -1.0, 0.0]),
            np.array([1.0, -2.0, 0.0]),
        ]
    )

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([0.0, 1.0, 0.0])
    assert q == pytest.approx([0.0, -1.0, 0.0])


def test_get_closest_points_with_parallel_non_collinear_tie_on_second_segments() -> (
    None
):
    # Both wires are multi-segment and the tie-break fires between each wire's second
    # segment. Guards against iteration-depth bugs.
    #
    # first:  (-3,1)->(-2,1)->(-2,0)   (horizontal to x=-2, then vertical down to y=0)
    # second: ( 3,1)->( 2,1)->( 2,0)   (same shape mirrored — vertical at x=2 is seg1)
    #
    # (first.seg0, second.seg0): horizontal y=1 vs horizontal y=1, collinear. Closest
    # (-2,1) and (2,1), dist²=16. Sets best.
    # (first.seg0, second.seg1): horizontal y=1 vs vertical x=2, perpendicular.
    # Closest (-2,1) and (2,1), dist²=16. Non-parallel, no tie-break.
    # (first.seg1, second.seg0): vertical x=-2 vs horizontal y=1, perpendicular.
    # Closest (-2,1) and (2,1), dist²=16. Non-parallel, no tie-break.
    # (first.seg1, second.seg1): vertical x=-2 vs vertical x=2, parallel, NOT collinear.
    # y-overlap [0,1]; midpoint (-2,0.5) and (2,0.5), dist²=16. Tie + parallel
    # -> overrides.
    first = manual_wire_from_vertices(
        [
            np.array([-3.0, 1.0, 0.0]),
            np.array([-2.0, 1.0, 0.0]),
            np.array([-2.0, 0.0, 0.0]),
        ]
    )
    second = manual_wire_from_vertices(
        [
            np.array([3.0, 1.0, 0.0]),
            np.array([2.0, 1.0, 0.0]),
            np.array([2.0, 0.0, 0.0]),
        ]
    )

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([-2.0, 0.5, 0.0])
    assert q == pytest.approx([2.0, 0.5, 0.0])


def test_get_closest_points_with_parallel_non_coll_tie_self_second_other_first() -> (
    None
):
    # The tie-break fires between self's second segment and other's first (and only)
    # segment. Guards against iteration-asymmetry bugs.
    #
    # first:  (3,1)->(3,-1)->(1,-1)   (seg0: vertical at x=3; seg1: horizontal y=-1)
    # second: (0,0)->(2,0)            (single segment: horizontal at y=0)
    #
    # (first.seg0, second.seg0): vertical x=3 vs horizontal y=0, perpendicular.
    # Closest (3,0,0) (on vertical, y=0 in range) and (2,0,0) (clamped to end),
    # dist²=1. Sets best.
    # (first.seg1, second.seg0): horizontal y=-1 vs horizontal y=0, parallel, NOT
    # collinear. x-overlap [1,2]; midpoint (1.5,-1,0) and (1.5,0,0), dist²=1.
    # Tie + parallel -> overrides.
    first = manual_wire_from_vertices(
        [
            np.array([3.0, 1.0, 0.0]),
            np.array([3.0, -1.0, 0.0]),
            np.array([1.0, -1.0, 0.0]),
        ]
    )
    second = manual_wire_from_vertices(
        [
            np.array([0.0, 0.0, 0.0]),
            np.array([2.0, 0.0, 0.0]),
        ]
    )

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([1.5, -1.0, 0.0])
    assert q == pytest.approx([1.5, 0.0, 0.0])


def test_get_closest_points_with_collinear_endpoints_does_not_trigger_override() -> (
    None
):
    # Two collinear (co-axial) segments with a gap: the expected endpoint-to-endpoint
    # result is returned and the collinear guard correctly suppresses the tie-break.
    # This explicitly documents the collinear-guard contract: a parallel + collinear
    # pair must never trigger the `<=` override branch.
    #
    # first:  (0,0)->(1,0)     (horizontal at y=0)
    # second: (3,0)->(4,0)     (horizontal at y=0, collinear, 2-unit gap)
    first = manual_wire_from_vertices(
        [
            np.array([0.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
        ]
    )
    second = manual_wire_from_vertices(
        [
            np.array([3.0, 0.0, 0.0]),
            np.array([4.0, 0.0, 0.0]),
        ]
    )

    p, q = first.get_closest_points_with(second)

    assert p == pytest.approx([1.0, 0.0, 0.0])
    assert q == pytest.approx([3.0, 0.0, 0.0])
