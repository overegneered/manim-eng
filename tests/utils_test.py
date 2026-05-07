import copy

import numpy as np
import pytest

from manim_eng._utils import utils

STANDARD_MARGIN = np.deg2rad(5)


@pytest.mark.parametrize(
    ("vector", "margin", "expected"),
    [
        pytest.param([1, 1, 0], STANDARD_MARGIN, [1, 1, 0], id="no action necessary"),
        pytest.param(
            [9.99048222, 0.43619387, 0],
            STANDARD_MARGIN,
            [10, 0, 0],
            id="snapped vectors maintain magnitude",
        ),
        pytest.param(
            [0.9961947, 0.08715574, 0],
            STANDARD_MARGIN,
            [1, 0, 0],
            id="on positive margin (right)",
        ),
        pytest.param(
            [0.9961947, -0.08715574, 0],
            STANDARD_MARGIN,
            [1, 0, 0],
            id="on negative margin (right)",
        ),
        pytest.param(
            [-0.9961947, 0.08715574, 0],
            STANDARD_MARGIN,
            [-1, 0, 0],
            id="on negative margin (left)",
        ),
        pytest.param(
            [-0.9961947, -0.08715574, 0],
            STANDARD_MARGIN,
            [-1, 0, 0],
            id="on positive margin (left)",
        ),
        pytest.param(
            [0.08715574, 0.9961947, 0],
            STANDARD_MARGIN,
            [0, 1, 0],
            id="on negative margin (up)",
        ),
        pytest.param(
            [-0.08715574, 0.9961947, 0],
            STANDARD_MARGIN,
            [0, 1, 0],
            id="on positive margin (up)",
        ),
        pytest.param(
            [-0.08715574, -0.9961947, 0],
            STANDARD_MARGIN,
            [0, -1, 0],
            id="on negative margin (down)",
        ),
        pytest.param(
            [0.08715574, -0.9961947, 0],
            STANDARD_MARGIN,
            [0, -1, 0],
            id="on positive margin (down)",
        ),
    ],
)
def test_cardinalised(
    vector: list[float],
    margin: float,
    expected: list[float],
) -> None:
    vector_original = copy.deepcopy(vector)

    result = utils.cardinalised(vector, margin)

    assert np.allclose(result, expected)
    assert np.all(vector == vector_original)


@pytest.mark.parametrize(
    ("vector", "expected"),
    [
        pytest.param([1, 0, 0], True, id="RIGHT"),
        pytest.param([0, 1, 0], True, id="UP"),
        pytest.param([0, 0, 1], True, id="OUT"),
        pytest.param([-1, 0, 0], True, id="LEFT"),
        pytest.param([0, -1, 0], True, id="DOWN"),
        pytest.param([3, 0, 0], True, id="non-unit cardinal magnitude"),
        pytest.param([1, 1, 0], False, id="diagonal"),
        pytest.param([0.99, 0.01, 0], False, id="nearly-cardinal"),
        pytest.param([0, 0, 0], False, id="zero vector"),
    ],
)
def test_is_cardinal(vector: list[float], expected: bool) -> None:
    assert utils.is_cardinal(vector) == expected


@pytest.mark.parametrize(
    ("vector", "expected"),
    [
        pytest.param([1, 0, 0], [1, 0, 0], id="no action necessary"),
        pytest.param(
            [0.7071067811865475, 0.7071067811865475, 0],
            [1, 0, 0],
            id="45 degrees snaps to the vertical preferentially",
        ),
    ],
)
def test_cardinalised_no_margin_given(
    vector: list[float], expected: list[float]
) -> None:
    result = utils.cardinalised(vector)

    assert np.allclose(result, expected)


# --------------------------------------------------------------------------------------
# closest_points_of_two_line_segments
# --------------------------------------------------------------------------------------


def test_closest_points_both_segments_degenerate() -> None:
    # Both segments collapse to single points.
    p, q = utils.closest_points_of_two_line_segments(
        np.array([1.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([4.0, 0.0, 0.0]),
        np.array([4.0, 0.0, 0.0]),
    )

    assert p == pytest.approx([1.0, 0.0, 0.0])
    assert q == pytest.approx([4.0, 0.0, 0.0])


def test_closest_points_first_segment_degenerate() -> None:
    # First segment is a point; closest point on the second is computed.
    p, q = utils.closest_points_of_two_line_segments(
        np.array([0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0]),
        np.array([-1.0, 1.0, 0.0]),
        np.array([1.0, 1.0, 0.0]),
    )

    assert p == pytest.approx([0.0, 0.0, 0.0])
    assert q == pytest.approx([0.0, 1.0, 0.0])


def test_closest_points_second_segment_degenerate() -> None:
    # Second segment is a point; closest point on the first is computed.
    p, q = utils.closest_points_of_two_line_segments(
        np.array([-1.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 2.0, 0.0]),
        np.array([0.0, 2.0, 0.0]),
    )

    assert p == pytest.approx([0.0, 0.0, 0.0])
    assert q == pytest.approx([0.0, 2.0, 0.0])


def test_closest_points_crossing_segments() -> None:
    # Two segments that intersect; distance should be zero.
    p, q = utils.closest_points_of_two_line_segments(
        np.array([-1.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, -1.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
    )

    assert p == pytest.approx([0.0, 0.0, 0.0])
    assert q == pytest.approx([0.0, 0.0, 0.0])


def test_closest_points_skew_segments() -> None:
    # One segment along the x-axis, the other along z offset by (0,1,0).
    p, q = utils.closest_points_of_two_line_segments(
        np.array([0.0, 0.0, 0.0]),
        np.array([2.0, 0.0, 0.0]),
        np.array([1.0, 1.0, -1.0]),
        np.array([1.0, 1.0, 1.0]),
    )

    assert p == pytest.approx([1.0, 0.0, 0.0])
    assert q == pytest.approx([1.0, 1.0, 0.0])


def test_closest_points_parallel_overlapping() -> None:
    # Overlap interval is [1, 2]; midpoint on each is (1.5, 0, 0).
    p, q = utils.closest_points_of_two_line_segments(
        np.array([0.0, 0.0, 0.0]),
        np.array([2.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([3.0, 0.0, 0.0]),
    )

    assert p == pytest.approx([1.5, 0.0, 0.0])
    assert q == pytest.approx([1.5, 0.0, 0.0])


def test_closest_points_parallel_non_overlapping() -> None:
    # Gap between the segments; closest points are the facing endpoints.
    p, q = utils.closest_points_of_two_line_segments(
        np.array([0.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([3.0, 0.0, 0.0]),
        np.array([4.0, 0.0, 0.0]),
    )

    assert p == pytest.approx([1.0, 0.0, 0.0])
    assert q == pytest.approx([3.0, 0.0, 0.0])


def test_closest_points_anti_parallel_overlapping() -> None:
    # Same geometry as parallel_overlapping but with the second segment reversed.
    p, q = utils.closest_points_of_two_line_segments(
        np.array([0.0, 0.0, 0.0]),
        np.array([2.0, 0.0, 0.0]),
        np.array([3.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
    )

    assert p == pytest.approx([1.5, 0.0, 0.0])
    assert q == pytest.approx([1.5, 0.0, 0.0])


def test_closest_points_t_clamps_to_zero() -> None:
    # Unclamped t would be negative; closest point on second segment is its start.
    p, q = utils.closest_points_of_two_line_segments(
        np.array([0.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([0.5, 2.0, 0.0]),
        np.array([0.5, 3.0, 0.0]),
    )

    assert p == pytest.approx([0.5, 0.0, 0.0])
    assert q == pytest.approx([0.5, 2.0, 0.0])


def test_closest_points_t_clamps_to_one() -> None:
    # Unclamped t would exceed 1; closest point on second segment is its end.
    p, q = utils.closest_points_of_two_line_segments(
        np.array([0.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([0.5, -3.0, 0.0]),
        np.array([0.5, -2.0, 0.0]),
    )

    assert p == pytest.approx([0.5, 0.0, 0.0])
    assert q == pytest.approx([0.5, -2.0, 0.0])


# --------------------------------------------------------------------------------------
# are_parallel
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("vec_a", "vec_b", "expected"),
    [
        pytest.param([1, 0, 0], [2, 0, 0], True, id="same_direction"),
        pytest.param([1, 0, 0], [-3, 0, 0], True, id="opposite_direction"),
        pytest.param([1, 0, 0], [0, 1, 0], False, id="perpendicular"),
        pytest.param([1, 1, 0], [2, 2, 0], True, id="diagonal_parallel"),
        pytest.param([1, 1, 0], [1, -1, 0], False, id="diagonal_not_parallel"),
        pytest.param([0, 0, 1], [0, 0, 5], True, id="3d_vectors"),
        pytest.param([0, 0, 0], [1, 0, 0], True, id="zero_vector"),
    ],
)
def test_are_parallel(
    vec_a: list[float],
    vec_b: list[float],
    expected: bool,
) -> None:
    result = utils.are_parallel(np.array(vec_a), np.array(vec_b))

    assert result == expected


def test_are_parallel_nearly_parallel_returns_false() -> None:
    # Cross product magnitude of 2e-8 is just outside np.allclose default atol of 1e-8.
    vec_a = np.array([1.0, 0.0, 0.0])
    vec_b = np.array([1.0, 2e-8, 0.0])

    result = utils.are_parallel(vec_a, vec_b)

    assert result is False


# --------------------------------------------------------------------------------------
# are_collinear
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("start", "direction", "target", "expected"),
    [
        pytest.param(
            np.array([0, 0, 0]),
            np.array([1, 0, 0]),
            np.array([3, 0, 0]),
            True,
            id="point_on_line",
        ),
        pytest.param(
            np.array([0, 0, 0]),
            np.array([1, 0, 0]),
            np.array([3, 1, 0]),
            False,
            id="point_off_line",
        ),
        pytest.param(
            np.array([0, 0, 0]),
            np.array([1, 0, 0]),
            np.array([-2, 0, 0]),
            True,
            id="point_behind_start",
        ),
        pytest.param(
            np.array([0, 0, 0]),
            np.array([1, 0, 0]),
            np.array([0, 0, 0]),
            True,
            id="point_is_start",
        ),
        pytest.param(
            np.array([0, 0, 0]),
            np.array([1, 1, 0]),
            np.array([2, 2, 0]),
            True,
            id="diagonal_on_line",
        ),
        pytest.param(
            np.array([0, 0, 0]),
            np.array([1, 1, 0]),
            np.array([2, 1, 0]),
            False,
            id="diagonal_off_line",
        ),
        pytest.param(
            np.array([0, 0, 0]),
            np.array([0, 0, 1]),
            np.array([0, 0, 4]),
            True,
            id="3d_line_on",
        ),
        pytest.param(
            np.array([0, 0, 0]),
            np.array([0, 0, 1]),
            np.array([1, 0, 4]),
            False,
            id="3d_line_off",
        ),
    ],
)
def test_are_collinear(
    start: np.ndarray,
    direction: np.ndarray,
    target: np.ndarray,
    expected: bool,
) -> None:
    result = utils.are_collinear(start, direction, target)

    assert result == expected
