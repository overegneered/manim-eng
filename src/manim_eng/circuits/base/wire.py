"""Wire implementation class."""

import abc
from typing import Any

import manim as mn
from manim import typing as mnt

from manim_eng import config_eng
from manim_eng.circuits.current import CurrentArrow
from manim_eng.components.base.pin import Pin

__all__ = ["WireBase"]


class WireBase(mn.VMobject, metaclass=abc.ABCMeta):
    """Base class for wire objects.

    Subclasses must implement the :meth:`~.WireBase.get_corner_points()` method to
    declare where the wire corners should be.
    """

    def __init__(self, start: Pin, end: Pin, updating: bool):
        super().__init__(stroke_width=config_eng.symbol.wire_stroke_width)

        if start == end:
            raise ValueError(
                "`start` and `end` are identical. "
                "Wires must have different pins at each end."
            )

        self._start = start
        self._end = end
        self.add(self._start, self._end)

        self.__update_points()

        self._current = CurrentArrow(self)
        self.add(self._current)

        self._attached = False

        if updating:
            self.add_updater(lambda mob: mob.__update_points())

    @property
    def current(self) -> CurrentArrow:
        """A current arrow attached to the wire."""
        return self._current

    def __update_points(self) -> None:
        # The extra points involving the 0.001 factors extend the wire ever so slightly
        # into the terminals, producing a nice clean join between the terminals and the
        # wire
        self.set_points_as_corners(
            [
                self._start.base,
                self._start.tip,
                *self.get_corner_points(),
                self._end.tip,
                self._end.base,
            ]
        )

    @abc.abstractmethod
    def get_corner_points(self) -> list[mnt.Point3D]:
        """Get the corner points of the wire.

        Returns the vertices of the wire, not including the end points (i.e. at the
        start and end terminals).
        """

    @mn.override_animation(mn.Create)
    def __override_create(self, **kwargs: Any) -> mn.Animation:
        self.animate(**kwargs).attach()
        return mn.Create(self, use_override=False, **kwargs)

    @mn.override_animation(mn.Uncreate)
    def __override_uncreate(self, **kwargs: Any) -> mn.Animation:
        self.animate(**kwargs).detach()
        return mn.Uncreate(self, use_override=False, **kwargs)
