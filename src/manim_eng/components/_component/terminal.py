from typing import Self

import manim as mn
import manim.typing as mnt
import numpy as np

from ..._config import config_eng
from ..._debug.anchor import Anchor
from .mark import Mark, Markable


class CurrentArrow(mn.Triangle):
    def __init__(self, position: mnt.Vector3D, rotation: float = 0) -> None:
        super().__init__(
            radius=config_eng.symbol.current_arrow_radius,
            start_angle=rotation,
            color=mn.WHITE,
            fill_color=mn.WHITE,
            fill_opacity=1,
        )
        self.move_to(position)


class Terminal(Markable):
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
    debug : bool
        Whether to enable the debug visuals.
    """

    def __init__(
        self, position: mnt.Vector3D, direction: mnt.Vector3D, debug: bool = False
    ):
        super().__init__(debug)

        direction /= np.linalg.norm(direction)
        end = position - (direction * config_eng.symbol.terminal_length)
        self.line = mn.Line(
            start=position,
            end=end,
            stroke_width=config_eng.symbol.wire_stroke_width,
        )
        self.add(self.line)

        self.position = position
        self.direction = direction

        self._current_anchor: Anchor = Anchor(config_eng.anchor.current_colour)
        self._centre_anchor: Anchor = Anchor(config_eng.anchor.centre_colour).move_to(
            self.get_center()
        )

        self.angle_offset = np.arccos(np.dot(direction, np.array([1, 0, 0])))
        self._current_arrow: CurrentArrow = CurrentArrow(
            self._centre_anchor.pos, self.angle_offset
        )
        self._current_arrow_showing: bool = False
        self._current_arrow_pointing_out: bool = True

        self._current_anchor.move_to(self._current_arrow.get_top())
        self._current: Mark = Mark(self._current_anchor, self._centre_anchor)

        self.add(self._centre_anchor, self._current_anchor)

    def set_current(self, label: str, out: bool = False, below: bool = False) -> Self:
        """Set the current annotation of the terminal.

        Parameters
        ----------
        label : str
            The current label to set. Takes a TeX math mode string.
        out : bool
            Whether the arrow accompanying the annotation should point out (away from
            the body of the component to which the terminal is attached), or in (towards
            the component, this is the default).
        below : bool
            Whether the annotation should be placed below the current arrow, or above it
            (which is the default). Note that 'below' here is for when the component is
            unrotated.

        Returns
        -------
        Self
            The (modified) terminal on which the method was called.
        """
        if not self._current_arrow_showing:
            self.add(self._current_arrow)
            self._current_arrow_showing = True
        if out != self._current_arrow_pointing_out:
            self._current_arrow.rotate(np.pi)
            self._current_arrow_pointing_out = out
        if below:
            self._current_anchor.move_to(self._current_arrow.get_bottom())
        else:
            self._current_anchor.move_to(self._current_arrow.get_top())
        self._set_mark(self._current, label)
        return self

    def clear_current(self) -> Self:
        """Clear the current annotation of the terminal.

        Returns
        -------
        Self
            The (modified) terminal on which the method was called.
        """
        self.remove(self._current_arrow)
        self._current_arrow_showing = False
        self._clear_mark(self._current)
        return self
