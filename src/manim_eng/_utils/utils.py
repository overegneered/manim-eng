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
