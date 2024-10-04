"""Wire implementation class."""

import abc

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
