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
from manim_eng.circuits.node import Node
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


# TODO: make this a subclass of Markable to move the label control stuff into it
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
        if hasattr(self, "_start") and self._start.attached_wire is self:
            self._start.detach_wire()
        if hasattr(self, "_end") and self._end.attached_wire is self:
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
    def pins(self) -> tuple[Pin, Pin]:
        """The pins connected to the wire."""
        return self.start, self.end

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

    @abc.abstractmethod
    def on_split(
        self, first_end: Pin, second_start: Pin, alpha: float
    ) -> tuple[Self, Self]:
        """Set up a split for the wire.

        This is used by :meth:`~.WireBase.split_at` and friends to implement the actual
        splitting of wires, and should be implemented by subclasses. The pins passed in,
        ``first_end`` and ``second_start``, are on the node constructed by the caller.
        All this method needs to do is construct the two shapes of the wires and set
        up updaters if necessary. Things like current arrow transferral are handled by
        the caller.

        This method **does not** need to handle wire detachment.
        :meth:`~.Pin.detach_wire`. That is handled

        Parameters
        ----------
        first_end : Pin
            The end of the first segment (the start is the same as the start of the
            original wire)
        second_start : Pin
            The start of the second segment (the end is the same as the end of the
            original wire)
        alpha : float
            Where the split occured, as a proportion of the distance along the wire from
            the start to the end. Always between 0 and 1.

        Returns
        -------
        tuple[Self, Self]
            The two new segments, ordered from start to end with respect to the original
            wire sense.

        See Also
        --------
        split_at
        """
        raise NotImplementedError

    def split_at(
        self,
        alpha: float,
        container: mn.Scene | mn.Mobject | None = None,
    ) -> tuple[Self, Node, Self]:
        """Split the wire a given point, inserting a node at the split point.

        The direction of the wire is maintained.

        If the wire has an active current arrow, it is automatically placed on
        whichever half it geometrically falls on based on its current ``alpha``
        value, and its ``alpha`` is remapped so that its visual position along
        that half is unchanged. If the split is directly over the current arrow, the
        segment for which the start is maintained is given it.

        Parameters
        ----------
        alpha : float
            The point to split the wire at, as a proportion of the wire length.
        container : Scene | Mobject, optional
            If provided, the original wire is removed from ``container`` and the
            two new wire portions and the node are added to it. **If not used, this
            process will have to be completed manually.**

        Returns
        -------
        tuple[Self, Node, Self]
            A three-element tuple of ``(start_portion, node, end_portion)``.

            * ``start_portion`` — the first half of the wire as a new object,
              retaining the original start pin.
            * ``node`` — the node inserted at the split point.
            * ``end_portion`` — the second half of the wire as a new object,
              retaining the original end pin.

        Raises
        ------
        ValueError
            If ``alpha`` is not between 0 and 1 exclusive.

        See Also
        --------
        split_at_corner
        split_at_corners
        """
        if not (0 < alpha < 1):
            raise ValueError(
                f"`alpha` must be strictly between 0 and 1 (exclusive), got {alpha!r}."
            )
        epsilon = 1e-6
        split_point = self.point_from_proportion(alpha)
        towards_start = self.point_from_proportion(alpha - epsilon)
        towards_end = self.point_from_proportion(alpha + epsilon)

        current_is_active = self._current._triangle in self._current.submobjects
        if current_is_active:
            tex_strings = self._current._label.tex_strings
            # tex_strings is set when the triangle is active
            assert tex_strings is not None
            current_label: str = tex_strings[0]
            current_alpha: float = self._current._alpha
            current_invert: bool = self._current._invert

        self._start.detach_wire()
        self._end.detach_wire()

        node = Node().move_to(split_point)
        start_portion, end_portion = self.on_split(
            node.get(towards_start - split_point),
            node.get(towards_end - split_point),
            alpha,
        )

        if current_is_active:
            # When invert=True, _alpha is measured from the end of the wire, so the
            # true geometric position from the start is (1 - current_alpha).
            geometric_pos = (1 - current_alpha) if current_invert else current_alpha

            if geometric_pos <= alpha:
                new_geom_alpha = geometric_pos / alpha
                new_alpha = (1 - new_geom_alpha) if current_invert else new_geom_alpha
                start_portion.current.set(
                    label=current_label, alpha=new_alpha, invert=current_invert
                )
            else:
                new_geom_alpha = (geometric_pos - alpha) / (1 - alpha)
                new_alpha = (1 - new_geom_alpha) if current_invert else new_geom_alpha
                end_portion.current.set(
                    label=current_label, alpha=new_alpha, invert=current_invert
                )

        if container is not None:
            container.remove(self)
            container.add(start_portion, node, end_portion)

        return start_portion, node, end_portion

    def split_at_point(
        self,
        point: mnt.Point3D,
        container: mn.Scene | mn.Mobject | None = None,
    ) -> tuple[Self, Node, Self]:
        """Split the wire at ``point`` and return the new resulting objects.

        If the wire intersects with itself and the intersection point is supplied, only
        the first point when walking from the start to the end is used.

        Parameters
        ----------
        point : mnt.Point3D
            The point to split the wire at. Must lie on the wire.
        container : Scene | Mobject, optional
            If provided, the original wire is removed from ``container`` and the
            two new wire portions and the node are added to it. **If not used, this
            process will have to be completed manually.**

        Returns
        -------
        tuple[Self, Node, Self]
            A three-element tuple of ``(start_portion, node, end_portion)``.

            * ``start_portion`` — the first half of the wire as a new object,
              retaining the original start pin.
            * ``node`` — the node inserted at the split point.
            * ``end_portion`` — the second half of the wire as a new object,
              retaining the original end pin.

        Raises
        ------
        ValueError
            If ``point`` does not lie on the wire.
        """
        alpha = self.get_alpha_at_point(point)
        if alpha is None:
            raise ValueError(f"The given point {point} does not lie on the wire")
        return self.split_at(alpha, container=container)

    def split_at_corner(
        self,
        index: int,
        container: mn.Scene | mn.Mobject | None = None,
    ) -> tuple[Self, Node, Self]:
        """Split the wire at a single corner given by index.

        Parameters
        ----------
        index : int
            The index of the corner to split at. Supports negative indexing.
            Corners are ordered from start to end, matching
            :meth:`~.Wire.get_corner_points`.
        container : Scene | Mobject, optional
            If provided, the original wire is removed from ``container`` and the
            two new wire portions and the node are added to it. **If not used, this
            process will have to be completed manually.**

        Returns
        -------
        tuple[Self, Node, Self]
            A three-element tuple of ``(start_portion, node, end_portion)``.

            * ``start_portion`` — the first half of the wire as a new object,
              retaining the original start pin.
            * ``node`` — the node inserted at the split point.
            * ``end_portion`` — the second half of the wire as a new object,
              retaining the original end pin.

        Raises
        ------
        ValueError
            If the wire has no corners.
        IndexError
            If ``index`` is out of range for the number of corners on the wire.

        See Also
        --------
        split_at
        split_at_corners
        """
        corner_points = self.get_corner_points()
        n_corners = len(corner_points)

        if n_corners == 0:
            raise ValueError("This wire has no corners to split at.")
        if not (-n_corners <= index < n_corners):
            raise IndexError(
                f"Corner index {index!r} is out of range for a wire with "
                f"{n_corners} corner(s)."
            )

        return self.split_at_point(corner_points[index], container=container)

    def split_at_corners(
        self, container: mn.Scene | mn.Mobject | None = None
    ) -> tuple[list[Self], list[Node]]:
        """Split the wire at its visual corners except those at pin tips.

        Splits the wire at the points given by :meth:`~.Wire.get_corner_points`.

        Parameters
        ----------
        container : Scene | Mobject, optional
            If provided, the original wire is removed from ``container`` and the new
            wire portions and nodes are added to it. **If not used, this process will
            have to be completed manually.**

        Returns
        -------
        tuple[list[Self], list[Node]]
            A two-element tuple containing:

            * A list of new wire segments in order from start to end.
            * A list of new nodes in order from start to end.

        See Also
        --------
        split_at
        split_at_corner
        """
        n_corners = len(self.get_corner_points())  # snapshot BEFORE any splits
        if n_corners == 0:
            return [self], []

        segments: list[Self] = []
        nodes: list[Node] = []
        remaining = self

        for _ in range(n_corners):
            segment, node, remaining = remaining.split_at_corner(0)
            segments.append(segment)
            nodes.append(node)

        segments.append(remaining)

        if container is not None:
            container.remove(self)
            container.add(*segments, *nodes)

        return segments, nodes

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

        Where multiple segments are of identical closeness, segments that are parallel
        and not collinear are preferred. This is to produce the 'logical' closest
        points. Consider the example below::

            +---+       +---+
                |       |
                *       *
                |       |
            +---+       +---+

        The points marked with asterisks ``*`` are those a human would generally pick if
        connecting those two wires with another wire. Without the carve-out for
        parallelism and non collinearity, the corners would be chosen due to the order
        the line segments are iterated through.
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
                segments_parallel = utils.are_parallel(
                    self_segment[1] - self_segment[0],
                    other_segment[1] - other_segment[0],
                )
                segments_collinear = utils.are_collinear(
                    self_segment[0], self_segment[1] - self_segment[0], other_segment[0]
                )
                if dist < best_dist or (
                    dist <= best_dist and segments_parallel and not segments_collinear
                ):
                    best_point_self = point_self
                    best_point_other = point_other
                    best_dist = dist

        return best_point_self, best_point_other

    def get_alpha_at_point(self, point: mnt.Point3D) -> float | None:
        """Get the proportion of the wire from the start to ``point``.

        Parameters
        ----------
        point : mnt.Point3D
            The point to query.

        Returns
        -------
        float | None
            If the point lies on the wire, returns the proportion of the wire (alpha)
            between ``self.start.base`` and ``point``. If not, returns ``None``.
        """
        all_vertices = self.get_all_vertices()
        lengths = [
            float(np.linalg.norm(b - a)) for a, b in itertools.pairwise(all_vertices)
        ]

        total_length = sum(lengths)
        length_to_point = 0.0

        for (start, end), length in zip(
            itertools.pairwise(all_vertices), lengths, strict=True
        ):
            segment_vector = end - start
            point_vector = point - start

            if utils.are_parallel(segment_vector, point_vector) and np.all(
                0
                <= np.dot(segment_vector, point_vector)
                <= np.dot(segment_vector, segment_vector)
            ):
                length_to_point += float(np.linalg.norm(point_vector))
                return length_to_point / total_length
            length_to_point += length
        return None

    def coincident_with(self, point: mnt.Point3D) -> bool:
        """Compute whether ``point`` lies along the wire.

        Parameters
        ----------
        point : mnt.Point3D
            The point to query.

        Returns
        -------
        bool
            ``True`` if the point lies on the wire, ``False`` otherwise.

        See Also
        --------
        get_alpha_at_point
        """
        return self.get_alpha_at_point(point) is not None

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
