"""Contains Pin class."""

from typing import TYPE_CHECKING, Self

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng._base.anchor import PinAnchor
from manim_eng._base.markable import Markable
from manim_eng._config import config_eng
from manim_eng.circuits.current import CurrentArrow

if TYPE_CHECKING:
    from manim_eng.circuits.base.wire import WireBase

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
        direction = mn.normalize(direction)

        if length is None:
            length = config_eng.symbol.pin_length

        self._body_anchor = PinAnchor().move_to(position)
        self._end_anchor = PinAnchor().move_to(position + direction * length)

        self.add(self._body_anchor, self._end_anchor)

        self._attached_wire: WireBase | None = None

    @property
    def base(self) -> mnt.Point3D:
        """The point at which the pin connects to the component body."""
        return self._body_anchor.pos

    @property
    def tip(self) -> mnt.Point3D:
        """The point at which the pin connects to external wires."""
        return self._end_anchor.pos

    @property
    def direction(self) -> mnt.Vector3D:
        """A unit vector pointing out of the pin (towards the end)."""
        return mn.normalize(self.tip - self.base)

    @property
    def length(self) -> float:
        """The length of the pin (the distance between the start and end)."""
        return float(np.linalg.norm(self.tip - self.base))

    @property
    def attached_wire(self) -> "WireBase | None":
        """A reference to the wire attached to this pin, if one exists."""
        return self._attached_wire

    @property
    def current(self) -> CurrentArrow:
        """A handle to the current arrow on the wire attached to this pin.

        Raises
        ------
        AttributeError
            If no wire is attached to this pin.
        """
        if self._attached_wire is None:
            raise AttributeError("No wire attached to this pin.")
        return self._attached_wire.current

    def attach_wire(self, wire: "WireBase") -> Self:
        """Register that a wire is attached to this pin.

        Does nothing if the wire is already attached.

        Parameters
        ----------
        wire : WireBase
            The wire to be attached.

        Raises
        ------
        AttributeError
            If a wire not equal to ``wire`` is already attached to this pin.
        """
        if self._attached_wire is not None and self._attached_wire != wire:
            raise AttributeError(
                "A pin can only have one wire attached at any given"
                "time. Please add a node to handle wire junctions."
            )
        self._attached_wire = wire
        return self

    def detach_wire(self) -> Self:
        """Register that the attached wire has been detached.

        Does nothing if no wire was attached in the first place.
        """
        self._attached_wire = None
        return self

    def is_visible(self) -> bool:
        """Return whether the pin appears drawn on screen, to the best of its knowledge.

        Returns
        -------
        bool
            ``True`` if the pin is visible, ``False`` otherwise.
        """
        if self._attached_wire is None:
            return False
        return self._attached_wire.is_visible()
