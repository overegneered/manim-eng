"""Wire implementation class."""

import abc
from typing import Any, Self, cast

import manim as mn
import numpy as np
from manim import typing as mnt

from manim_eng import config_eng
from manim_eng.circuits.current import CurrentArrow
from manim_eng.components.base.pin import Pin

__all__ = ["WireBase"]


class _WireShowMixin(mn.Animation):
    """Mixin for creation animations: marks the wire shown when the animation begins."""

    def begin(self) -> None:
        wire = cast("WireBase", self.mobject)
        wire._set_visible()
        super().begin()


class _WireHideMixin(mn.Animation):
    """Mixin for destruction animations: marks the wire hidden when animation ends."""

    def finish(self) -> None:
        super().finish()
        wire = cast("WireBase", self.mobject)
        wire._set_hidden()


class _CreateWire(_WireShowMixin, mn.Create): ...


class _FadeInWire(_WireShowMixin, mn.FadeIn): ...


class _WriteWire(_WireShowMixin, mn.Write): ...


class _DrawBorderThenFillWire(_WireShowMixin, mn.DrawBorderThenFill): ...


class _GrowFromCenterWire(_WireShowMixin, mn.GrowFromCenter): ...


class _GrowFromPointWire(_WireShowMixin, mn.GrowFromPoint): ...


class _GrowFromEdgeWire(_WireShowMixin, mn.GrowFromEdge): ...


class _SpinInFromNothingWire(_WireShowMixin, mn.SpinInFromNothing): ...


class _SpiralInWire(_WireShowMixin, mn.SpiralIn): ...


class _UncreateWire(_WireHideMixin, mn.Uncreate): ...


class _FadeOutWire(_WireHideMixin, mn.FadeOut): ...


class _UnwriteWire(_WireHideMixin, mn.Unwrite): ...


class _ShrinkToCenterWire(_WireHideMixin, mn.ShrinkToCenter): ...


class WireBase(mn.VMobject, metaclass=abc.ABCMeta):
    """Base class for wire objects.

    Subclasses must implement the :meth:`~.WireBase.get_corner_points()` method to
    declare where the wire corners should be.
    """

    def __init__(self, start: Pin, end: Pin, updating: bool) -> None:
        super().__init__(stroke_width=config_eng.symbol.wire_stroke_width)

        if start == end:
            raise ValueError(
                "`start` and `end` are identical. "
                "Wires must have different pins at each end."
            )

        self._start = start
        self._end = end
        self._visible: bool = False

        self._start.attach_wire(self)
        self._end.attach_wire(self)

        WireBase._update_points(self)

        self._current = CurrentArrow(self)
        self.add(self._current)

        if updating:
            self.add_updater(WireBase._update_points)

    def __del__(self) -> None:
        """Clean up wire attachments on deletion."""
        self._start.detach_wire()
        self._end.detach_wire()

    @property
    def start(self) -> Pin:
        """The start pin of the wire."""
        return self._start

    @property
    def end(self) -> Pin:
        """The end pin of the wire."""
        return self._end

    @property
    def current(self) -> CurrentArrow:
        """A current arrow attached to the wire."""
        return self._current

    @abc.abstractmethod
    def get_corner_points(self) -> list[mnt.Point3D]:
        """Get the corner points of the wire.

        Returns the vertices of the wire, not including the end points (i.e. the start
        and end pins).

        Returns
        -------
        list[Point3D]
            The corner points of the wire between the two pins, in order from start
            to end.
        """

    @staticmethod
    def _update_points(mob: mn.Mobject) -> None:
        wire = cast("WireBase", mob)
        wire.set_points_as_corners(wire._get_full_corner_points())

    def _get_full_corner_points(self) -> list[mnt.Point3D]:
        """Get the full ordered point list for this wire, including pin bases and tips.

        Builds the complete sequence of points, then cleans it up by removing duplicate
        adjacent points and collinear points that lie outside their neighbours (i.e.
        backtracking paths that look straight on screen but would cause animation
        glitches).

        Returns
        -------
        list[Point3D]
            The filtered set of corners points
        """
        points = [
            self._start.base,
            self._start.tip,
            *self.get_corner_points(),
            self._end.tip,
            self._end.base,
        ]

        i = 0
        while i < len(points) - 2:
            a, b, c = points[i], points[i + 1], points[i + 2]

            # Cut out duplicates
            if np.allclose(a, b) or np.allclose(b, c):
                del points[i + 1]
                continue

            # Cut out backtracking collinear paths that appear direct on screen
            ab = b - a
            ac = c - a
            if np.allclose(np.cross(ab, ac), np.zeros(3)):
                ac_sq = np.dot(ac, ac)
                if not np.isclose(ac_sq, 0):
                    t = np.dot(ab, ac) / ac_sq
                    if not (0 <= t <= 1):
                        del points[i + 1]
                        continue
            i += 1

        return points

    def is_visible(self) -> bool:
        """Return if the wire is visible."""
        return self._visible

    def _set_visible(self) -> Self:
        """Mark this wire as currently visible.

        See Also
        --------
        _set_hidden
        """
        self._visible = True
        return self

    def _set_hidden(self) -> Self:
        """Mark this wire as currently hidden.

        See Also
        --------
        _set_visible
        """
        self._visible = False
        return self

    @mn.override_animation(mn.Create)
    def __override_create(self, **kwargs: Any) -> mn.Animation:
        return _CreateWire(self, **kwargs)

    @mn.override_animation(mn.FadeIn)
    def __override_fade_in(self, **kwargs: Any) -> mn.Animation:
        return _FadeInWire(self, **kwargs)

    @mn.override_animation(mn.Write)
    def __override_write(self, **kwargs: Any) -> mn.Animation:
        return _WriteWire(self, **kwargs)

    @mn.override_animation(mn.DrawBorderThenFill)
    def __override_draw_border_then_fill(self, **kwargs: Any) -> mn.Animation:
        return _DrawBorderThenFillWire(self, **kwargs)

    @mn.override_animation(mn.GrowFromCenter)
    def __override_grow_from_center(self, **kwargs: Any) -> mn.Animation:
        return _GrowFromCenterWire(self, **kwargs)

    @mn.override_animation(mn.GrowFromPoint)
    def __override_grow_from_point(self, **kwargs: Any) -> mn.Animation:
        return _GrowFromPointWire(self, **kwargs)

    @mn.override_animation(mn.GrowFromEdge)
    def __override_grow_from_edge(self, **kwargs: Any) -> mn.Animation:
        return _GrowFromEdgeWire(self, **kwargs)

    @mn.override_animation(mn.SpinInFromNothing)
    def __override_spin_in_from_nothing(self, **kwargs: Any) -> mn.Animation:
        return _SpinInFromNothingWire(self, **kwargs)

    @mn.override_animation(mn.SpiralIn)
    def __override_spiral_in(self, **kwargs: Any) -> mn.Animation:
        return _SpiralInWire(self, **kwargs)

    @mn.override_animation(mn.Uncreate)
    def __override_uncreate(self, **kwargs: Any) -> mn.Animation:
        return _UncreateWire(self, **kwargs)

    @mn.override_animation(mn.FadeOut)
    def __override_fade_out(self, **kwargs: Any) -> mn.Animation:
        return _FadeOutWire(self, **kwargs)

    @mn.override_animation(mn.Unwrite)
    def __override_unwrite(self, **kwargs: Any) -> mn.Animation:
        return _UnwriteWire(self, **kwargs)

    @mn.override_animation(mn.ShrinkToCenter)
    def __override_shrink_to_center(self, **kwargs: Any) -> mn.Animation:
        return _ShrinkToCenterWire(self, **kwargs)
