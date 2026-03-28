"""Wire and related implementation classes."""

from typing import Self, Sequence, cast

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng._utils import utils
from manim_eng.circuits.base.wire import WireBase
from manim_eng.circuits.node import Node
from manim_eng.components.base.pin import Pin

__all__ = ["ManualWire", "Wire"]


class ManualWire(WireBase):
    """Wire that requires its path to be manually specified.

    Parameters
    ----------
    start : Pin
        The pin the wire starts at.
    end : Pin
        The pin the wire ends at.
    corner_points : Sequence[Point3D], optional
        The vertices the wire should have between the two pins. Should not include
        the positions of the two pins, as these are inserted automatically when the
        wire is drawn. These should be in order from ``start`` to ``end``. If left
        unspecified, the wire will directly connect the start and end pins.
    updating : bool
        Whether the ends of the wire should update automatically to keep connected to
        the pins. This is disabled by default. If this is enabled, it is recommended to
        attach another updater that will update ``corner_points`` to prevent strange
        artefacts.

    Raises
    ------
    ValueError
        If ``start`` and ``end`` are the same.
    """

    def __init__(
        self,
        start: Pin,
        end: Pin,
        corner_points: Sequence[mnt.Point3D] | None = None,
        updating: bool = False,
    ):
        self._corner_points = list(corner_points) if corner_points is not None else []
        super().__init__(start, end, updating)

    def get_corner_points(self) -> list[mnt.Point3D]:
        """Get the corner points of the wire.

        Returns the vertices of the wire, not including the points at which the wires
        connect to the components themselves (i.e. the pin bases).

        Returns
        -------
        list[Point3D]
            The corner points of the wire between the two pin bases, in order from start
            to end.
        """
        return self._corner_points

    def set_corner_points(self, points: Sequence[mnt.Point3D]) -> Self:
        """Set the corner points of the wire.

        Parameters
        ----------
        points : Sequence[Point3D]
            The vertices the wire should have between the two pin bases. Should not
            include the points at which the wires connect to the components themselves,
            but should include all other points.

        Notes
        -----
        :attr:`~.Pin.tip` may be helpful when placing points if you want to ensure wires
        always have some distance straight out from a component's body.
        """
        self._corner_points = list(points)
        return self


class Wire(WireBase):
    """Wire to automatically connect components together.

    The connection algorithm will do its best to avoid going 'backwards' through
    components' pins whilst ensuring that automatic connections have no more than
    two vertices and are only horizontal and vertical.

    Parameters
    ----------
    start : Pin
        The pin the wire starts at.
    end : Pin
        The pin the wire ends at.

    Raises
    ------
    ValueError
        If ``start`` and ``end`` are the same.
    """

    def __init__(self, start: Pin, end: Pin) -> None:
        super().__init__(start, end, updating=True)

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
        start_portion = Wire(self._start, node.get(towards_start - split_point))
        end_portion = Wire(node.get(towards_end - split_point), self._end)

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
        index = index % n_corners

        all_vertices = self.get_all_vertices()

        cumulative = [0.0]
        for i in range(len(all_vertices) - 1):
            dist = float(np.linalg.norm(all_vertices[i + 1] - all_vertices[i]))
            cumulative.append(cumulative[-1] + dist)
        total = cumulative[-1]
        # Bump index by one to skip over initial cumulative element with value 0
        alpha = cumulative[1 + index] / total

        return self.split_at(alpha, container=container)

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

    def get_corner_points(self) -> list[mnt.Point3D]:
        """Get the corner points of the wire.

        Returns the vertices of the wire, not including the points at which the wires
        connect to the components themselves (i.e. the pin bases). Vertices for the pin
        tips are only included where they would be visible corners (i.e. the pin is not
        in a cardinal direction but the wire coming out of it is).

        Returns
        -------
        list[Point3D]
            The corner points of the wire between the two pin bases, in order from start
            to end.
        """
        intersection = mn.find_intersection(
            [self._start.base],
            [self._start.direction],
            [self._end.base],
            [self._end.direction],
        )[0]

        start_proj = np.dot(intersection - self._start.base, self._start.direction)
        end_proj = np.dot(intersection - self._end.base, self._end.direction)
        start_is_cardinal = utils.is_cardinal(self._start.direction)
        end_is_cardinal = utils.is_cardinal(self._end.direction)

        intersection_in_front = start_proj >= 0 and end_proj >= 0
        cardinal_or_intersection_in_pin = (
            start_is_cardinal or start_proj <= self._start.length
        ) and (end_is_cardinal or end_proj <= self._end.length)
        # mn.find_intersection() returns p0s when the lines are parallel
        parallel_but_pins_collinear = np.isclose(
            np.dot(self._start.direction, self._end.direction), 0
        ) and np.isclose(
            np.dot(self._start.direction, self._start.base - self._end.base), 0
        )

        if parallel_but_pins_collinear or (
            intersection_in_front and cardinal_or_intersection_in_pin
        ):
            return [intersection]

        from_direction = utils.cardinalised(self._start.direction)
        to_direction = utils.cardinalised(self._end.direction)

        if np.isclose(np.dot(from_direction, to_direction), 0):
            corner_points = self.__get_corner_points_for_perpendicular_pins(
                from_direction, to_direction
            )
        else:
            corner_points = self.__get_corner_points_for_parallel_pins(
                from_direction, to_direction
            )

        if not start_is_cardinal:
            corner_points.insert(0, self._start.tip)
        if not end_is_cardinal:
            corner_points.append(self._end.tip)

        return corner_points

    def __get_corner_points_for_perpendicular_pins(
        self, from_direction: mnt.Vector3D, to_direction: mnt.Vector3D
    ) -> list[mnt.Point3D]:
        from_end = self._start.tip
        to_end = self._end.tip

        corner_point = mn.find_intersection(
            [from_end], [from_direction], [to_end], [to_direction]
        )[0]

        if self.__point_is_behind_plane(
            corner_point, from_end, from_direction
        ) or self.__point_is_behind_plane(corner_point, to_end, to_direction):
            # Move the corner point to the other vertex of the box formed from the end
            # of each pin, as two 90 degree turns at a component is better than one
            # 0 degree and one 180 degree.
            if corner_point[0] == from_end[0]:
                corner_point = np.array([to_end[0], from_end[1], 0])
            else:
                corner_point = np.array([from_end[0], to_end[1], 0])

        return [corner_point]

    def __get_corner_points_for_parallel_pins(
        self, from_direction: mnt.Vector3D, to_direction: mnt.Vector3D
    ) -> list[mnt.Point3D]:
        midpoint = mn.midpoint(self._start.tip, self._end.tip)

        to_behind_from = self.__point_is_behind_plane(
            self._end.tip, self._start.tip, from_direction
        )
        from_behind_to = self.__point_is_behind_plane(
            self._start.tip, self._end.tip, to_direction
        )

        if to_behind_from and from_behind_to:
            # This is necessary to prevent the line from going backwards through the
            # components
            from_direction = mn.rotate_vector(from_direction, np.pi / 2)
            to_direction = mn.rotate_vector(to_direction, np.pi / 2)
        # These two are to handle the case where two pins point in the same
        # direction, so we really want an elbow rather than an 'S'
        elif to_behind_from:
            midpoint = self.__move_point_forward_of_plane(
                midpoint, self._start.tip, from_direction
            )
        elif from_behind_to:
            midpoint = self.__move_point_forward_of_plane(
                midpoint, self._end.tip, to_direction
            )

        perpendicular_direction = np.cross(from_direction, mn.OUT)
        return cast(
            list[mnt.Point3D],
            mn.find_intersection(
                [midpoint] * 2,
                [perpendicular_direction] * 2,
                [self._start.tip, self._end.tip],
                [from_direction, to_direction],
            ),
        )

    @staticmethod
    def __point_is_behind_plane(
        point: mnt.Point3D, point_on_plane: mnt.Point3D, normal: mnt.Vector3D
    ) -> bool:
        """Return whether a given point is behind a specified plane.

        Parameters
        ----------
        point : Point3D
            The point to check.
        point_on_plane : Point3D
            A point on the plane against which to check.
        normal : Vector3D
            The normal vector of the plane against which to check.

        Returns
        -------
        bool
            ``True`` if the point is behind the plane, ``False`` if it is not.
        """
        vector_to_point = point - point_on_plane
        return cast(bool, np.dot(normal, vector_to_point) < 0)

    @staticmethod
    def __move_point_forward_of_plane(
        point: mnt.Point3D, point_on_plane: mnt.Point3D, normal: mnt.Vector3D
    ) -> mnt.Point3D:
        """Move a given point such that it lies on or in front of a specified plane.

        Parameters
        ----------
        point : Point3D
            The point to move.
        point_on_plane : Point3D
            A point on the plane.
        normal : Vector3D
            The normal vector of the plane

        Returns
        -------
        Point3D
            The new point.
        """
        vector_to_point = point - point_on_plane
        distance_to_move = -np.dot(normal, vector_to_point)
        if distance_to_move <= 0:
            # No movement is necessary
            return point
        return point + mn.normalize(normal) * distance_to_move
