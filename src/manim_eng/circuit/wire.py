"""Module containing the Wire class."""

from typing import cast

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng import config_eng
from manim_eng._base.terminal import Terminal
from manim_eng._utils import utils


class Wire(mn.VMobject):
    """Wire to connect components together.

    The connection algorithm will do its best to avoid going 'backwards' through
    components' terminals whilst ensuring that automatic connections have no more than
    two vertices and are only horizontal and vertical.

    Parameters
    ----------
    from_terminal : Terminal
        The terminal the wire comes from.
    to_terminal : Terminal
        The terminal the wire goes to.
    """

    def __init__(self, from_terminal: Terminal, to_terminal: Terminal) -> None:
        super().__init__(stroke_width=config_eng.symbol.wire_stroke_width)

        self.from_terminal = from_terminal
        self.to_terminal = to_terminal

        self.add_updater(self.__shape_updater)
        self.update()

    def __shape_updater(self, _mobject: mn.Mobject) -> None:
        from_direction = utils.cardinalised(self.from_terminal.direction)
        to_direction = utils.cardinalised(self.to_terminal.direction)

        if np.isclose(np.dot(from_direction, to_direction), 0):
            corner_points = self.__get_corner_points_for_perpendicular_terminals(
                from_direction, to_direction
            )
        else:
            corner_points = self.__get_corner_points_for_parallel_terminals(
                from_direction, to_direction
            )

        # The extra points involving the 0.001 factors extend the wire ever so slightly
        # into the terminals, producing a nice clean join between the terminals and the
        # wire
        self.set_points_as_corners(
            [
                self.from_terminal.end - self.from_terminal.direction * 0.001,
                self.from_terminal.end,
                *corner_points,
                self.to_terminal.end,
                self.to_terminal.end - self.to_terminal.direction * 0.001,
            ]
        )

    def __get_corner_points_for_perpendicular_terminals(
        self, from_direction: mnt.Vector3D, to_direction: mnt.Vector3D
    ) -> list[mnt.Point3D]:
        from_end = self.from_terminal.end
        to_end = self.to_terminal.end

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
        midpoint = mn.midpoint(self.from_terminal.end, self.to_terminal.end)

        to_behind_from = self.__point_is_behind_plane(
            self.to_terminal.end, self.from_terminal.end, from_direction
        )
        from_behind_to = self.__point_is_behind_plane(
            self.from_terminal.end, self.to_terminal.end, to_direction
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
                midpoint, self.from_terminal.end, from_direction
            )
        elif from_behind_to:
            midpoint = self.__move_point_forward_of_plane(
                midpoint, self.to_terminal.end, to_direction
            )

        perpendicular_direction = np.cross(from_direction, mn.OUT)
        corner_points = mn.find_intersection(
            [midpoint] * 2,
            [perpendicular_direction] * 2,
            [self.from_terminal.end, self.to_terminal.end],
            [from_direction, to_direction],
        )
        return [*corner_points]

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
        return point + utils.normalised(normal) * distance_to_move
