"""Wire and related implementation classes."""

from typing import Self, Sequence, cast

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng._utils import utils
from manim_eng.circuits.base.wire import WireBase
from manim_eng.components.base.terminal import Terminal

__all__ = ["ManualWire", "Wire"]


class ManualWire(WireBase):
    """Wire that requires its path to be manually specified.

    Parameters
    ----------
    start : Terminal
        The terminal the wire starts at.
    end : Terminal
        The terminal the wire ends at.
    corner_points : Sequence[Point3D], optional
        The vertices the wire should have between the two terminals. Should not include
        the positions of the two terminals, as these are inserted automatically when the
        wire is drawn. These should be in order from ``start`` to ``end``. If left
        unspecified, this is taken to be ``[]`` and the wire will directly connect the
        start and end terminals.
    updating : bool
        Whether the ends of the wire should update automatically to keep connected to
        the terminals. This is disabled by default. If this is enabled, it is
        recommended to attach another updater that will update ``corner_points`` to
        prevent strange artefacts.

    Raises
    ------
    ValueError
        If ``start`` and ``end`` are the same.
    """

    def __init__(
        self,
        start: Terminal,
        end: Terminal,
        corner_points: Sequence[mnt.Point3D] | None = None,
        updating: bool = False,
    ):
        self._corner_points = list(corner_points) if corner_points is not None else []
        super().__init__(start, end, updating)

    def get_corner_points(self) -> list[mnt.Point3D]:
        """Get the corner points of the wire.

        Returns the vertices of the wire, not including the end points (i.e. at the
        start and end terminals).
        """
        return self._corner_points

    def set_corner_points(self, points: Sequence[mnt.Point3D]) -> Self:
        """Set the corner points of the wire.

        Parameters
        ----------
        points : Sequence[Point3D]
            The vertices the wire should have between the two terminals. Should not
            include the positions of the two terminals, as these are inserted
            automatically when the wire is drawn. These should be in order from
            ``start`` to ``end``.
        """
        self._corner_points = list(points)
        return self


class Wire(WireBase):
    """Wire to automatically connect components together.

    The connection algorithm will do its best to avoid going 'backwards' through
    components' terminals whilst ensuring that automatic connections have no more than
    two vertices and are only horizontal and vertical.

    Parameters
    ----------
    start : Terminal
        The terminal the wire starts at.
    end : Terminal
        The terminal the wire ends at.

    Raises
    ------
    ValueError
        If ``start`` and ``end`` are the same.
    """

    def __init__(self, start: Terminal, end: Terminal) -> None:
        super().__init__(start, end, updating=True)

    def get_corner_points(self) -> list[mnt.Point3D]:
        """Get the corner points of the wire.

        Returns the vertices of the wire, not including the end points (i.e. at the
        start and end terminals).
        """
        from_direction = utils.cardinalised(self.start.direction)
        to_direction = utils.cardinalised(self.end.direction)

        if np.isclose(np.dot(from_direction, to_direction), 0):
            return self.__get_corner_points_for_perpendicular_terminals(
                from_direction, to_direction
            )
        return self.__get_corner_points_for_parallel_terminals(
            from_direction, to_direction
        )

    def __get_corner_points_for_perpendicular_terminals(
        self, from_direction: mnt.Vector3D, to_direction: mnt.Vector3D
    ) -> list[mnt.Point3D]:
        from_end = self.start.end
        to_end = self.end.end

        corner_point = mn.find_intersection(
            [from_end], [from_direction], [to_end], [to_direction]
        )[0]

        if self.__point_is_behind_plane(
            corner_point, from_end, from_direction
        ) or self.__point_is_behind_plane(corner_point, to_end, to_direction):
            # Move the corner point to the other vertex of the box formed from the end
            # of each terminal, as two 90 degree turns at a component is better than one
            # 0 degree and one 180 degree.
            if corner_point[0] == from_end[0]:
                corner_point = np.array([to_end[0], from_end[1], 0])
            else:
                corner_point = np.array([from_end[0], to_end[1], 0])

        return [corner_point]

    def __get_corner_points_for_parallel_terminals(
        self, from_direction: mnt.Vector3D, to_direction: mnt.Vector3D
    ) -> list[mnt.Point3D]:
        midpoint = mn.midpoint(self.start.end, self.end.end)

        to_behind_from = self.__point_is_behind_plane(
            self.end.end, self.start.end, from_direction
        )
        from_behind_to = self.__point_is_behind_plane(
            self.start.end, self.end.end, to_direction
        )

        if to_behind_from and from_behind_to:
            # This is necessary to prevent the line from going backwards through the
            # components
            from_direction = mn.rotate_vector(from_direction, np.pi / 2)
            to_direction = mn.rotate_vector(to_direction, np.pi / 2)
        # These two are to handle the case where two terminals point in the same
        # direction, so we really want an elbow rather than an 'S'
        elif to_behind_from:
            midpoint = self.__move_point_forward_of_plane(
                midpoint, self.start.end, from_direction
            )
        elif from_behind_to:
            midpoint = self.__move_point_forward_of_plane(
                midpoint, self.end.end, to_direction
            )

        perpendicular_direction = np.cross(from_direction, mn.OUT)
        corner_points = mn.find_intersection(
            [midpoint] * 2,
            [perpendicular_direction] * 2,
            [self.start.end, self.end.end],
            [from_direction, to_direction],
        )
        return list(corner_points)

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
            The new plane.
        """
        vector_to_point = point - point_on_plane
        distance_to_move = -np.dot(normal, vector_to_point)
        if distance_to_move <= 0:
            # No movement is necessary
            return point
        return point + mn.normalize(normal) * distance_to_move
