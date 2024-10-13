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

    def __init__(self, from_terminal: Terminal, to_terminal: Terminal, updating: bool):
        super().__init__(stroke_width=config_eng.symbol.wire_stroke_width)

        if from_terminal == to_terminal:
            raise ValueError(
                "`from_terminal` and `to_terminal` are identical. "
                "Wires must have different terminals at each end."
            )

        self.from_terminal = from_terminal
        self.to_terminal = to_terminal

        self.__construct_wire()

        if updating:
            self.add_updater(lambda mob: mob.__construct_wire())

    def attach(self) -> Self:
        """Attach the wire to the terminals it goes to and from.

        This updates the terminals so that they know they have one more connection.
        """
        self.from_terminal._increment_connection_count()
        self.to_terminal._increment_connection_count()
        return self

    def detach(self) -> Self:
        """Detach the wire from the terminals it goes to and from.

        This updates the terminals so that they know they have one fewer connection.
        """
        self.from_terminal._decrement_connection_count()
        self.to_terminal._decrement_connection_count()
        return self

    def __construct_wire(self) -> None:
        # The extra points involving the 0.001 factors extend the wire ever so slightly
        # into the terminals, producing a nice clean join between the terminals and the
        # wire
        self.set_points_as_corners(
            [
                self.from_terminal.end - 0.001 * self.from_terminal.direction,
                self.from_terminal.end,
                *self.get_corner_points(),
                self.to_terminal.end,
                self.to_terminal.end - 0.001 * self.to_terminal.direction,
            ]
        )

    @abc.abstractmethod
    def get_corner_points(self) -> list[mnt.Point3D]:
        """Get the corner points of the wire.

        Returns the vertices of the wire, not including the end points (i.e. at the
        start and end terminals).
        """

    # TODO: #18 overrides for all creation and destruction methods that play the
    #       terminal animations (and increment/decrement the terminal counts!)
    #       BEWARE the terminal counts currently incremented on lines 30 and 31!

    @mn.override_animate(attach)
    def __animate_attach(self, anim_args: dict[str, Any] | None = None) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return mn.AnimationGroup(
            self.from_terminal.animate(**anim_args)._increment_connection_count(),
            self.to_terminal.animate(**anim_args)._increment_connection_count(),
        )

    @mn.override_animate(detach)
    def __animate_detach(self, anim_args: dict[str, Any] | None = None) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return mn.AnimationGroup(
            self.from_terminal.animate(**anim_args)._decrement_connection_count(),
            self.to_terminal.animate(**anim_args)._decrement_connection_count(),
        )

    @mn.override_animation(mn.Create)
    def __override_create(self, **kwargs: Any) -> mn.Animation:
        return mn.AnimationGroup(
            self.animate(**kwargs).attach(),
            mn.Create(self, use_override=False),
        )

    @mn.override_animation(mn.Uncreate)
    def __override_uncreate(self, **kwargs: Any) -> mn.Animation:
        return mn.AnimationGroup(
            self.animate(**kwargs).detach(),
            mn.Uncreate(self, use_override=False),
        )
