"""Wire and related implementation classes."""

import itertools
from typing import Self, Sequence, cast

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng._utils import utils
from manim_eng.circuits.base.wire import WireBase
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

    def on_split(
        self, first_end: Pin, second_start: Pin, alpha: float
    ) -> tuple[Self, Self]:
        """Split this wire into two at the given arc-length proportion.

        Parameters
        ----------
        first_end : Pin
            The end of the first segment.
        second_start : Pin
            The start of the second segment.
        alpha : float
            How far along the wire it has been split.

        Returns
        -------
        tuple[ManualWire, ManualWire]
            The two segments the wire has been split into, in order from start to end.

        Warnings
        --------
        This disregards all updaters, since it is impossible to know how they should be
        copied over.
        """
        vertices = self.get_all_vertices()
        lengths: list[float] = [0.0]
        for start, end in itertools.pairwise(vertices):
            segment_length = float(np.linalg.norm(end - start))
            lengths.append(lengths[-1] + segment_length)

        cumulative_lengths = np.array(lengths)
        alpha_as_length = float(cumulative_lengths[-1]) * alpha
        alpha_index = int(np.sum(cumulative_lengths < alpha_as_length))

        # If the split falls exactly on an intermediate vertex, that vertex becomes the
        # node and should not appear as a corner in either half.
        at_vertex = alpha_index < len(cumulative_lengths) and bool(
            np.isclose(alpha_as_length, cumulative_lengths[alpha_index])
        )
        start_corners = vertices[1:alpha_index]
        end_corners = vertices[alpha_index + (1 if at_vertex else 0) : -1]

        start_portion = ManualWire(self._start, first_end, start_corners)
        end_portion = ManualWire(second_start, self._end, end_corners)

        return start_portion, end_portion

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

    def on_split(
        self, first_end: Pin, second_start: Pin, _alpha: float
    ) -> tuple[Self, Self]:
        """See :meth:`~.WireBase.on_split`."""
        start_portion = Wire(self._start, first_end)
        end_portion = Wire(second_start, self._end)
        return start_portion, end_portion

    def get_corner_points(self) -> list[mnt.Point3D]:
        """Get the corner points of the wire.

        Returns the vertices of the wire, not including the points at which the wires
        connect to the components themselves (i.e. the pin bases). Vertices are only
        included where they would be visible corners.

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
        parallel = utils.are_parallel(self._start.direction, self._end.direction)
        collinear = utils.are_collinear(
            self._start.base, self._start.direction, self._end.base
        )

        if parallel and collinear:
            return []
        if not parallel and intersection_in_front and cardinal_or_intersection_in_pin:
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
