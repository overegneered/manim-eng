"""Wire implementation class."""

import abc
from typing import Any, Self

import manim as mn
from manim import typing as mnt

from manim_eng import config_eng
from manim_eng.components.base import Terminal

__all__ = ["WireBase"]


class WireBase(mn.VMobject, metaclass=abc.ABCMeta):
    """Base class for wire objects.

    Subclasses must implement the ``.get_corner_points()`` method to declare where the
    wire should have corners.
    """

    def __init__(self, start: Terminal, end: Terminal, updating: bool):
        super().__init__(stroke_width=config_eng.symbol.wire_stroke_width)

        if start == end:
            raise ValueError(
                "`start` and `end` are identical. "
                "Wires must have different terminals at each end."
            )

        self.start = start
        self.end = end

        self._attached = False

        self.__construct_wire()

        if updating:
            self.add_updater(lambda mob: mob.__construct_wire())

    def attach(self) -> Self:
        """Attach the wire to its start and end terminals, if not already attached.

        This updates the terminals so that they know they have one more connection.
        """
        if not self._attached:
            self.start._increment_connection_count()
            self.end._increment_connection_count()
            self._attached = True
        return self

    def detach(self) -> Self:
        """Detach the wire from its start and end terminals, if not already detached.

        This updates the terminals so that they know they have one fewer connection.
        """
        if self._attached:
            self.start._decrement_connection_count()
            self.end._decrement_connection_count()
            self._attached = False
        return self

    def __construct_wire(self) -> None:
        # The extra points involving the 0.001 factors extend the wire ever so slightly
        # into the terminals, producing a nice clean join between the terminals and the
        # wire
        self.set_points_as_corners(
            [
                self.start.end - 0.001 * self.start.direction,
                self.start.end,
                *self.get_corner_points(),
                self.end.end,
                self.end.end - 0.001 * self.end.direction,
            ]
        )

    @abc.abstractmethod
    def get_corner_points(self) -> list[mnt.Point3D]:
        """Get the corner points of the wire.

        Returns the vertices of the wire, not including the end points (i.e. at the
        start and end terminals).
        """

    @mn.override_animate(attach)
    def __animate_attach(self, anim_args: dict[str, Any] | None = None) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return mn.AnimationGroup(
            self.start.animate(**anim_args)._increment_connection_count(),
            self.end.animate(**anim_args)._increment_connection_count(),
        )

    @mn.override_animate(detach)
    def __animate_detach(self, anim_args: dict[str, Any] | None = None) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return mn.AnimationGroup(
            self.start.animate(**anim_args)._decrement_connection_count(),
            self.end.animate(**anim_args)._decrement_connection_count(),
        )

    @mn.override_animation(mn.Create)
    def __override_create(self, **kwargs: Any) -> mn.Animation:
        self.animate(**kwargs).attach()
        return mn.Create(self, use_override=False, **kwargs)

    @mn.override_animation(mn.Uncreate)
    def __override_uncreate(self, **kwargs: Any) -> mn.Animation:
        self.animate(**kwargs).detach()
        return mn.Uncreate(self, use_override=False, **kwargs)
