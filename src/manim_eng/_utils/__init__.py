import manim as mn
import manim.typing as mnt
import numpy as np


def normalised(vector: mnt.Vector3D) -> mnt.Vector3D:
    """Normalises the passed vector, and returns the result.

    Parameters
    ----------
    vector : Vector3D
        The vector to normalise.

    Returns
    -------
    Vector3D
        The resultant normalised vector.
    """
    return vector / np.linalg.norm(vector)


def small_values_zeroed_out(
    vector: mnt.Vector3D, tolerance: float = 0.0001
) -> mnt.Vector3D:
    """Return the input vector with smaller than ``tolerance`` zeroed-out.

    Parameters
    ----------
    vector : Vector3D
        The vector to start with.
    tolerance : float
        The maximum value for an element in ``vector`` that won't be set to zero.

    Returns
    -------
    Vector3D
        The resultant vector.
    """
    return vector * (np.abs(vector) > tolerance)


def cardinalised(vector: mnt.Vector3D, margin: float) -> mnt.Vector3D:
    """If ``vector`` is within ``margin`` of a cardinal direction, snap it to it.

    The angle the passed ``vector`` makes with the positive horizontal is checked, and
    if it falls within ``margin`` of a given cardinal direction, i.e. up, down, left, or
    right, then the vector is snapped to that cardinal direction, maintaining its
    original magnitude.

    Parameters
    ----------
    vector : mnt.Vector3D
        The vector to potentially snap to a cardinal direction.
    margin : float
        The maximum angle ``vector`` can make with a cardinal direction and still be
        snapped to it, in *radians*.

    Returns
    -------
    Vector3D
        The resultant vector.
    """
    vector_magnitude = np.linalg.norm(vector)
    angle = mn.angle_of_vector(vector)

    vector_within_margin_of_cardinal_direction = (angle + margin) % (
        np.pi / 2
    ) <= 2 * margin
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
