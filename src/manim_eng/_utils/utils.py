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
