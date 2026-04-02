"""Wire implementation class."""

import abc
import itertools
from typing import Any, Self, cast

import manim as mn
import numpy as np
from manim import typing as mnt

from manim_eng import config_eng
from manim_eng._utils import utils
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

        Returns the vertices of the wire, not including the points at which the wires
        connect to the components themselves (i.e. the pin bases). Must be overridden by
        subclasses.

        Returns
        -------
        list[Point3D]
            The corner points of the wire between the two pin bases, in order from start
            to end.
        """

    def get_all_vertices(self) -> list[mnt.Point3D]:
        """Get all vertices of the wire, including connection points.

        This includes the points at which the wire connects to the components, unlike
        :meth:`~.WireBase.get_corner_points`.

        Returns
        -------
        list[Point3D]
            The full list of vertices defining the shape of the wire.
        """
        return [self._start.base, *self.get_corner_points(), self._end.base]

    def get_point_closest_to(self, point: mnt.Point3D | Pin) -> mnt.Point3D:
        """Get the point on the wire closest to the given point.

        If multiple segments on the wire are equally close to ``point``, the segment
        earlier in the wire (closer to the start) will take priority.

        Parameters
        ----------
        point : Point3D | Pin
            The point to find the closest point to. If a ``Pin`` is provided, the point
            is taken to be the pin's tip.

        Returns
        -------
        Point3D
            A point on the wire closest to ``point``.
        """
        if isinstance(point, Pin):
            point = point.tip

        best_closest_point = mn.ORIGIN
        smallest_square_distance = np.inf

        for start, end in itertools.pairwise(self.get_all_vertices()):
            closest_point = utils.closest_point_on_line_segment_to_point(
                start, end, point
            )
            vector = point - closest_point
            square_distance = np.dot(vector, vector)

            if square_distance < smallest_square_distance:
                smallest_square_distance = square_distance
                best_closest_point = closest_point

        return best_closest_point

    def get_closest_points_with(
        self, other: "WireBase"
    ) -> tuple[mnt.Point3D, mnt.Point3D]:
        """Get the points on ``self`` and ``other`` that are closest to each other.

        Parameters
        ----------
        other : WireBase
            The wire to find the closest points to.

        Returns
        -------
        tuple[Point3D, Point3D]
            A two-element tuple containing the pair of points closest to each other. The
            first element is a point on ``self``, the second is a point on ``other``.

        Notes
        -----
        Uses the closest points of two line segments algorithm due to Ericson, as
        published in *Real-Time Collision Detection* (2005), §5.1.9.
        """
        best_point_self = mn.ORIGIN
        best_point_other = mn.ORIGIN
        best_dist = np.inf

        for self_segment in itertools.pairwise(self.get_all_vertices()):
            for other_segment in itertools.pairwise(other.get_all_vertices()):
                point_self, point_other = utils.closest_points_of_two_line_segments(
                    *self_segment, *other_segment
                )
                vector = point_other - point_self
                dist = np.dot(vector, vector)
                if dist < best_dist:
                    best_point_self = point_self
                    best_point_other = point_other
                    best_dist = dist

        return best_point_self, best_point_other

    @staticmethod
    def _update_points(mob: mn.Mobject) -> None:
        wire = cast("WireBase", mob)
        wire.set_points_as_corners(
            [
                wire._start.base,
                *wire.get_corner_points(),
                wire._end.base,
            ]
        )

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
