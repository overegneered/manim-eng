"""Contains Voltage class for drawing voltages between component terminals."""

from typing import Any, Self, cast

import manim as mn
import manim.typing as mnt
import numpy as np

import manim_eng._utils as utils
from manim_eng import config_eng
from manim_eng._base.anchor import CentreAnchor, VoltageAnchor
from manim_eng._base.mark import Mark
from manim_eng._base.markable import Markable
from manim_eng.components.base.terminal import Terminal

__all__ = ["Voltage"]


class Voltage(Markable):
    """Voltage arrow between two terminal endpoints.

    Parameters
    ----------
    from_terminal : Terminal
        The terminal the non-tip end of the arrow should be attached to, i.e. the
        'negative' end.
    to_terminal : Terminal
        The terminal the tip end of the arrow should be attached to, i.e. the 'positive'
        end.
    label : str
        The label for the voltage arrow. Takes a TeX math mode string.
    clockwise : bool
        Whether the arrow should go clockwise or anticlockwise. The default is
        anticlockwise.
    buff : float
        The buffer to use when attaching the arrow to the terminal ends.
    avoid : VMobject | None
        If a vmoject is specified, the arrow will go around it (including, if the
        vmobject is a component, labels or annotations attached to the component).
        If no component is specified, the arrow will take a default curvature.
    component_buff : float
        The buffer to use between the component body and the arrow, if a component to
        avoid is specified.
    """

    def __init__(
        self,
        from_terminal: Terminal,
        to_terminal: Terminal,
        label: str,
        clockwise: bool = False,
        buff: float = mn.SMALL_BUFF,
        avoid: mn.VMobject | None = None,
        component_buff: float = mn.SMALL_BUFF,
    ) -> None:
        super().__init__()

        self.from_terminal = from_terminal
        self.to_terminal = to_terminal
        self.clockwise = clockwise
        self.buff = buff
        self.component_to_avoid = avoid
        self.component_buff = component_buff

        self._direction = to_terminal.end - from_terminal.end
        self._angle_of_direction = mn.angle_of_vector(self._direction)

        self._arrow: mn.Arrow = mn.Arrow(mn.ORIGIN, mn.ORIGIN)
        self._centre_reference = CentreAnchor()
        self._anchor = VoltageAnchor()

        self.add_updater(lambda mob: mob.__arrow_updater())
        self.update()

        self.add(self._arrow, self._centre_reference, self._anchor)

        self._label = Mark(self._anchor, self._centre_reference)
        self._set_mark(self._label, label)

    def set_voltage(self, label: str) -> Self:
        """Set the voltage label.

        Parameters
        ----------
        label : str
            The label to set. Takes a TeX math mode string.
        """
        self._set_mark(self._label, label)
        return self

    def set_sense(self, clockwise: bool) -> Self:
        """Set the sense of the voltage arrow (clockwise or anticlockwise).

        Parameters
        ----------
        clockwise : bool
            Whether the arrow should be clockwise (``True``) or anticlockwise
            (``False``).
        """
        if clockwise == self.clockwise:
            return self
        self.clockwise = clockwise
        self.update()
        return self

    def set_from_terminal(self, terminal: Terminal) -> Self:
        """Set the terminal the arrow should point from.

        Parameters
        ----------
        terminal : Terminal
            The terminal that should be at the non-tip end of the voltage arrow.
        """
        self.from_terminal = terminal
        self.update()
        return self

    def set_to_terminal(self, terminal: Terminal) -> Self:
        """Set the terminal the arrow should point to.

        Parameters
        ----------
        terminal : Terminal
            The terminal that should be at the tip end of the voltage arrow.
        """
        self.to_terminal = terminal
        self.update()
        return self

    def flip_direction(self, flip_sense_as_well: bool = True) -> Self:
        """Flip the direction of the voltage arrow.

        Parameters
        ----------
        flip_sense_as_well : bool
            Whether to flip the sense of the arrow as well (clockwise to anticlockwise
            or anticlockwise to clockwise), so that the arrow remains on the same side
            of the component. Defaults to ``True``.
        """
        self.from_terminal, self.to_terminal = self.to_terminal, self.from_terminal
        if flip_sense_as_well:
            self.clockwise ^= True
        self.update()
        return self

    def __arrow_updater(self) -> None:
        self._direction = self.to_terminal.end - self.from_terminal.end
        self._angle_of_direction = mn.angle_of_vector(self._direction)

        self.__update_arrow()
        self.__update_anchors()

    def __update_arrow(self) -> None:
        if self.component_to_avoid is not None:
            middle_point = self._get_critical_point_at_different_rotation(
                self.component_to_avoid,
                mn.UP if self.clockwise else mn.DOWN,
                -self._angle_of_direction,
            )
            middle_point = self._introduce_buffer_to_point(
                middle_point, self.component_to_avoid.get_center(), self.component_buff
            )
            angle = self._get_arc_details_for_middle_point(middle_point)
        else:
            angle = config_eng.symbol.voltage_default_angle

        if self.clockwise:
            angle *= -1

        new_arrow = mn.Arrow(
            start=self.from_terminal.end,
            end=self.to_terminal.end,
            path_arc=angle,
            stroke_width=config_eng.symbol.arrow_stroke_width,
            tip_length=config_eng.symbol.arrow_tip_length,
            buff=self.buff,
        )
        self._arrow.become(new_arrow)

    def __update_anchors(self) -> None:
        top_of_arrow_bow = self._get_critical_point_at_different_rotation(
            self._arrow, mn.UP if self.clockwise else mn.DOWN, -self._angle_of_direction
        )

        self._centre_reference.move_to(self._arrow.get_center())
        self._anchor.move_to(top_of_arrow_bow)

    @staticmethod
    def _get_critical_point_at_different_rotation(
        mobject: mn.VMobject, direction: mnt.Vector3D, rotation: float
    ) -> mnt.Point3D:
        """Get a critical point on a mobject at a different rotation.

        Get, in global coordinates, the position a critical point given by
        ``direction`` would be on ``mobject`` if the component were rotated by
        ``rotation``. The passed mobject will be unaffected by this call.

        Parameters
        ----------
        mobject : VMobject
            The mobject to get a point on.
        direction : Vector3D
            The direction to use to find the critical point.
        rotation : float
            The amount to rotate the component before finding the critical point.

        Returns
        -------
        Point3D
            The coordinates of the point in global, unrotated coordinate space.
        """
        reference = mn.VMobject()
        reference.points = mobject.get_all_points()

        rotated_reference_critical_point = reference.rotate(
            rotation, about_point=mobject.get_center()
        ).get_critical_point(direction)
        relative_to_centre = rotated_reference_critical_point - mobject.get_center()
        return mobject.get_center() + mn.rotate_vector(relative_to_centre, -rotation)

    def _introduce_buffer_to_point(
        self, middle_point: mnt.Point3D, relative_to: mnt.Point3D, buff: float
    ) -> mnt.Point3D:
        """Add a buffer to the middle point, relative to the reference.

        Returns a new point that is ``buff`` further away from ``relative_to`` than
        ``middle_point``, in the same direction as ``middle_point``.

        Parameters
        ----------
        middle_point : Point3D
            The middle point.
        relative_to : Point3D
            The point to move ``middle_point`` away from.
        buff : float
            The buffer to move by

        Returns
        -------
        Point3D
            The new point.
        """
        relative_to_reference = middle_point - relative_to
        direction = utils.normalised(relative_to_reference)
        length = np.linalg.norm(relative_to_reference)
        return relative_to + direction * (length + buff)

    def _get_arc_details_for_middle_point(self, middle_point: mnt.Point3D) -> float:
        """Calculate the voltage arrow's arc to pass through ``middle_point``.

        Calculates the necessary angle to be swept by the voltage arrow's arc for it to
        pass through ``middle_point`` as well as its endpoints defined by the
        ``from_terminal`` and ``to_terminal`` as passed to the constructor.

        In all cases two possible angles are available, one reflex and one not. This
        method will always return the non-reflex one. As such, avoid passing in points
        that require reflex angles.

        Parameters
        ----------
        middle_point : Point3D
            The extra point the arrow should pass through, as well as the two end points
            defined by the ``from`` and ``to`` terminals.

        Returns
        -------
        tuple[float, float]
            A tuple consisting of the radius and angle necessary to make the arrow pass
            through ``middle_point``.

        Notes
        -----
        This implementation is only suitable for points that all have the same
        :math:`z`-ordinate.

        This uses the fact that an arc that passes through three points :math:`A`,
        :math:`B`, :math:`C` has a centre at the intersection of the perpendicular
        bisectors of the lines :math:`AB` and :math:`BC`. These can be found fairly
        easily by calculating the midpoint and the perpendicular vector.

        The intersection is then found using linear algebra, by forming simultaneous
        equations from the vector equations of the bisectors and solving for the scaling
        factors.
        """
        chord_ab = middle_point - self.from_terminal.end
        chord_bc = self.to_terminal.end - middle_point

        mid_ab = self.from_terminal.end + chord_ab / 2
        mid_bc = middle_point + chord_bc / 2

        perp_ab = np.cross(chord_ab, mn.OUT)
        perp_bc = np.cross(chord_bc, mn.OUT)

        # Solve for the intersection of the perpendicular bisectors using matrices
        matrix = np.array([[perp_ab[0], -perp_bc[0]], [perp_ab[1], -perp_bc[1]]])
        y = (mid_bc - mid_ab)[:2]
        x = np.linalg.inv(matrix) @ y

        # Find the centre using the vector equation for AB's bisector now that we know
        # the right value of 'alpha' (x[0])
        centre = mid_ab + x[0] * perp_ab

        radius = np.linalg.norm(centre - middle_point)
        length = np.linalg.norm(self._direction)
        return 2 * cast(float, np.arcsin(length / (2 * radius)))

    @mn.override_animate(set_voltage)
    def __animate_set_voltage(
        self, label: str, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return self.animate(**anim_args)._set_mark(self._label, label).build()
