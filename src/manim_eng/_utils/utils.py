"""Utilities for the rest of manim-eng."""

import manim as mn
import numpy as np
from manim import typing as mnt


def cardinalised(vector: mnt.Vector3D, margin: float | None = None) -> mnt.Vector3D:
    """If ``vector`` is within ``margin`` of a cardinal direction, snap it to it.

    The angle the passed ``vector`` makes with the positive horizontal is checked, and
    if it falls within ``margin`` of a given cardinal direction, i.e. up, down, left, or
    right, then the vector is snapped to that cardinal direction, maintaining its
    original magnitude.

    In the event that a vector lies perfectly on the boundary between possible snaps,
    the horizontal snap will be preferred.

    Parameters
    ----------
    vector : mnt.Vector3D
        The vector to potentially snap to a cardinal direction.
    margin : float
        The maximum angle ``vector`` can make with a cardinal direction and still be
        snapped to it, in *radians*. If not supplied, all vectors will be snapped to the
        nearest cardinal direction.

    Returns
    -------
    Vector3D
        The resultant vector.
    """
    vector_magnitude = np.linalg.norm(vector)
    angle = mn.angle_of_vector(vector)

    vector_within_margin_of_cardinal_direction = (
        (angle + margin) % (np.pi / 2) <= 2 * margin if margin is not None else True
    )
    if vector_within_margin_of_cardinal_direction:
        abs_max_index = np.argmax(np.abs(vector))
        cardinalised_vector = np.zeros_like(vector)
        # Flip the direction of the vector if necessary (i.e. if it's pointing left or
        # down)
        cardinalised_vector[abs_max_index] = vector_magnitude * np.sign(
            vector[abs_max_index]
        )
        return cardinalised_vector

    return vector


def is_cardinal(vector: mnt.Vector3D) -> bool:
    """Return whether a vector points in a cardinal direction.

    A cardinal direction is one aligned with an axis — i.e. a vector with only one
    non-zero element

    Parameters
    ----------
    vector : mnt.Vector3D
        The vector to check.

    Returns
    -------
    bool
        ``True`` if the vector is in a cardinal direction, ``False`` otherwise.
    """
    # Exactly two components must be zero (one non-zero = cardinal).
    # == 2 rather than >= 2 rejects the zero vector, which would give sum 3.
    # int() cast is required because np.isclose returns Any under mypy's numpy stubs,
    # which causes sum([Any, ...]) to also be Any.
    zeros: int = sum(
        [
            int(np.isclose(vector[0], 0)),
            int(np.isclose(vector[1], 0)),
            int(np.isclose(vector[2], 0)),
        ]
    )
    return zeros == 2  # noqa: PLR2004


def closest_points_of_two_line_segments(
    p0: mnt.Point3D,
    p1: mnt.Point3D,
    q0: mnt.Point3D,
    q1: mnt.Point3D,
) -> tuple[mnt.Point3D, mnt.Point3D]:
    """Compute the closest points of two given line segments.

    If the two segments are parallel and overlapping, selects the midpoints of the
    overlap.

    Parameters
    ----------
    p0 : Point3D
        The start of the first segment.
    p1 : Point3D
        The end of the first segment.
    q0 : Point3D
        The start of the second segment.
    q1 : Point3D
        The end of the second segment.

    Returns
    -------
    tuple[mnt.Point3D, mnt.Point3D]
        A two-element tuple consisting of the closest points on the two line segments.
        The point on segment (``p0``, ``p1``) is first, then the point on segment
        (``q0``, ``q1``).

    Notes
    -----
    Uses the closest points of two line segments algorithm due to Ericson, as published
    in *Real-Time Collision Detection* (2005), §5.1.9.

    See Also
    --------
    closest_point_on_line_segment_to_point
    """
    d1 = p1 - p0
    d2 = q1 - q0
    r = p0 - q0

    a = np.dot(d1, d1)
    e = np.dot(d2, d2)

    if np.isclose(a, 0) and np.isclose(e, 0):
        # Both segments degenerate
        return p0, q0

    f = np.dot(d2, r)
    if np.isclose(a, 0):
        # Segment (p0, p1) degenerate
        t = np.clip(f / e, 0, 1)
        return p0, q0 + t * d2

    c = np.dot(d1, r)
    if np.isclose(e, 0):
        # Segment (q0, q1) degenerate
        s = np.clip(-c / a, 0, 1)
        return p0 + s * d1, q0

    b = np.dot(d1, d2)
    denom = a * e - b * b

    if not np.isclose(denom, 0):
        # Non-parallel
        s = np.clip((b * f - c * e) / denom, 0, 1)
    else:
        # Parallel — select midpoint of overlap if the segments overlap, otherwise
        # fall back to the nearest endpoint of the first segment
        s0 = np.dot(q0 - p0, d1) / a
        s1 = np.dot(q1 - p0, d1) / a

        s_lo, s_hi = np.sort([s0, s1])
        overlap_lo = max(s_lo, 0)
        overlap_hi = min(s_hi, 1)
        s = (overlap_lo + overlap_hi) / 2 if overlap_lo <= overlap_hi else 0

    t = (b * s + f) / e

    if t < 0:
        t = 0
        s = np.clip(-c / a, 0, 1)
    elif t > 1:
        t = 1
        s = np.clip((b - c) / a, 0, 1)

    return p0 + s * d1, q0 + t * d2


def closest_point_on_line_segment_to_point(
    start: mnt.Point3D, end: mnt.Point3D, point: mnt.Point3D
) -> mnt.Point3D:
    """Compute the closest point on the line segment to point ``point``.

    Convenience wrapper around :meth:`closest_points_of_two_line_segments`.

    Parameters
    ----------
    start : mnt.Point3D
        The start point of the line segment.
    end : mnt.Point3D
        The end point of the line segment.
    point : mnt.Point3D
        The point to find the closest point on (``start``, ``end``) to.

    See Also
    --------
    closest_points_of_two_line_segments
    """
    closest_point, _ = closest_points_of_two_line_segments(start, end, point, point)
    return closest_point


def are_parallel(vec_a: mnt.Vector3D, vec_b: mnt.Vector3D) -> bool:
    """Return ``True`` if the vectors ``vec_a`` and ``vec_b`` are parallel."""
    return np.allclose(np.cross(vec_a, vec_b), 0)  # type: ignore[no-any-return]


def are_collinear(
    start: mnt.Point3D, direction: mnt.Vector3D, target: mnt.Point3D
) -> bool:
    """Calculate whether a point ``target`` is colinear with a line.

    Parameters
    ----------
    start : mnt.Point3D
        A point on the line.
    direction : mnt.Vector3D
        The direction of the line.
    target : mnt.Point3D
        The point to check for colinearity.

    Returns
    -------
    bool
        ``True`` if the ``target`` is colinear with the line (``start``, ``direction``).
    """
    return are_parallel(start - target, direction)
