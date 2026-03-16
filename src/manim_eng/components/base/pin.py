"""Contains Pin class."""

import manim.typing as mnt
import numpy as np

from manim_eng._base.anchor import TerminalAnchor
from manim_eng._base.markable import Markable
from manim_eng._config import config_eng

__all__ = ["Pin"]


class Pin(Markable):
    """Pin for a circuit component (i.e. the bit other wires connect to).

    Parameters
    ----------
    position : manim.Point3D
        The point at which the pin meets the body of the component.
    direction : manim.Vector3D
        A vector pointing in the direction of the pin (away from the body).
    length : float, optional
        The length the pin should have. If left unspecified, takes the value
        ``config_eng.symbol.pin_length``.
    """

    def __init__(
        self,
        position: mnt.Point3D,
        direction: mnt.Vector3D,
        length: float | None = None,
    ):
        super().__init__()
        direction /= np.linalg.norm(direction)

        if length is None:
            length = config_eng.symbol.pin_length

        self._body_anchor = TerminalAnchor().move_to(position)
        self._end_anchor = TerminalAnchor().move_to(position + direction * length)

    @property
    def start(self) -> mnt.Point3D:
        """The point at which the pin connects to the component body."""
        return self._body_anchor.pos

    @property
    def end(self) -> mnt.Point3D:
        """The point at which the pin connects to external wires."""
        return self._end_anchor.pos

    @property
    def direction(self) -> mnt.Vector3D:
        """A unit vector pointing out of the pin (towards the end)."""
        return (self.end - self.start) / self.length

    @property
    def length(self) -> float:
        """The length of the pin (the distance between the start and end)."""
        return float(np.linalg.norm(self.end - self.start))
