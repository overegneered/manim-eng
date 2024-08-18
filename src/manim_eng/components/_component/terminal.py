from typing import Self

import manim as mn
import manim.typing as mnt
import numpy as np

from .._component import WIRE_STROKE_WIDTH


class Terminal(mn.Line):
    """Terminal for a circuit component.

    Parameters
    ----------
    position : Vector3D
        The position of the *end* of the terminal, i.e. the bit that other components or
        wires would attach to.
    direction : Vector3D
        The direction the terminal 'points', i.e. the direction you get by walking from
        the point on the component body where the terminal attaches to the end of the
        terminal.
    """

    def __init__(self, position: mnt.Vector3D, direction: mnt.Vector3D):
        direction /= np.linalg.norm(direction)
        super().__init__(
            start=position,
            end=position - direction * 0.5,
            stroke_width=WIRE_STROKE_WIDTH,
        )

        self.position = position
        self.direction = direction

        self._current: mn.MathTex | None = None
