"""Contains Voltage class for drawing voltages between component terminals."""

from typing import Any, Self, cast

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng import config_eng
from manim_eng._base.anchor import CentreAnchor, VoltageAnchor
from manim_eng._base.mark import Mark
from manim_eng._base.markable import Markable
from manim_eng.components.base.terminal import Terminal
from manim_eng.units import Value

__all__ = ["Voltage"]


class Voltage(Markable):
    r"""Voltage arrow between two terminal endpoints.

    .. warning::
        manim-eng currently uses arcs of up to $\pi$ (180º) to build voltage arrows, so
        any label or annotation that requires an arc of more than a semicircle to get
        round it will result in overflow into an arc that is too small.

        This is a known issue and should be fixed in the 0.2 release by using polynomial
        arrow forms.

    Parameters
    ----------
    start : Terminal
        The terminal the non-tip end of the arrow should be attached to, i.e. the
        'negative' end.
    end : Terminal
        The terminal the tip end of the arrow should be attached to, i.e. the 'positive'
        end.
    label : str | Value
        The label for the voltage arrow. Takes a TeX math mode string, or a ``Value``
        to be typeset as a math mode string.
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
        start: Terminal,
        end: Terminal,
        label: str | Value,
        clockwise: bool = False,
        buff: float = mn.SMALL_BUFF,
        avoid: mn.VMobject | None = None,
        component_buff: float = 0.15,
    ) -> None:
        super().__init__()

        self.start = start
        self.end = end
        self.clockwise = clockwise
        self.buff = buff
        self.component_to_avoid = avoid
        self.component_buff = component_buff

        self._direction = end.end - start.end
        self._angle_of_direction = mn.angle_of_vector(self._direction)

        self._arrow: mn.Arrow = mn.Arrow(mn.ORIGIN, mn.ORIGIN)
        self._centre_reference = CentreAnchor()
        self._anchor = VoltageAnchor()

        self.add_updater(lambda mob: mob.__arrow_updater())
        self.update()

        self.add(self._arrow, self._centre_reference, self._anchor)

        self._label = Mark(self._anchor, self._centre_reference)
        self._set_mark(self._label, label)

    def set_label(self, label: str | Value, clockwise: bool | None = None) -> Self:
        """Set the voltage label.

        Parameters
        ----------
        label : str | Value
            The label to set. Takes a TeX math mode string, or a ``Value`` to be typeset
            as a math mode string.
        clockwise : bool | None
            Whether the arrow should go clockwise or anticlockwise. If unspecified,
            takes the previous setting.

        See Also
        --------
        reset_label: Set the voltage label, with the sense of the arrow being reset to
                     default if unspecified.
        """
        self._set_mark(self._label, label)
        if clockwise is not None:
            self.set_clockwise(clockwise=clockwise)
        return self

    def reset_label(self, label: str | Value, clockwise: bool = False) -> Self:
        """Set the voltage label, with the sense being reset to default if unspecified.

        Parameters
        ----------
        label : str | Value
            The label to set. Takes a TeX math mode string, or a ``Value`` to be typeset
            as a math mode string.
        clockwise : bool
            Whether the arrow should go clockwise or anticlockwise. If unspecified,
            takes the default setting (``False``).

        See Also
        --------
        set_label: Set the voltage label, with the sense of the arrow being left as-is
                   if unspecified.
        """
        return self.set_label(label=label, clockwise=clockwise)

    def set_clockwise(self, clockwise: bool = True) -> Self:
        """Set the sense of the voltage arrow (clockwise or anticlockwise).

        Parameters
        ----------
        clockwise : bool
            Whether the arrow should be clockwise (``True``) or anticlockwise
            (``False``). Defaults to clockwise.
        """
        if clockwise == self.clockwise:
            return self
        self.clockwise = clockwise
        self.update()
        return self

    def set_anticlockwise(self) -> Self:
        """Set the sense of the voltage arrow to be anticlockwise."""
        return self.set_clockwise(clockwise=False)

    def set_terminals(
        self, start: Terminal | None = None, end: Terminal | None = None
    ) -> Self:
        """Set the terminal(s) the arrow goes from/to.

        Parameters
        ----------
        start : Terminal | None
            The terminal to attach the start of the arrow to.
        end : Terminal | None
            The terminal to attach the end of the arrow to.

        Raises
        ------
        ValueError
            If neither `start` or `end` are specified.

        See Also
        --------
        set_start
        set_end
        """
        if start == end is None:
            raise ValueError("Neither `start` nor `end` specified.")
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end
        self.update()
        return self

    def set_start(self, terminal: Terminal) -> Self:
        """Set the terminal the arrow should start from.

        Parameters
        ----------
        terminal : Terminal
            The terminal that should be at the non-tip end of the voltage arrow.
        """
        return self.set_terminals(start=terminal)

    def set_end(self, terminal: Terminal) -> Self:
        """Set the terminal the arrow should point to.

        Parameters
        ----------
        terminal : Terminal
            The terminal that should be at the tip end of the voltage arrow.
        """
        return self.set_terminals(end=terminal)

    def flip_direction(self, flip_sense_as_well: bool = True) -> Self:
        """Flip the direction of the voltage arrow.

        Parameters
        ----------
        flip_sense_as_well : bool
            Whether to flip the sense of the arrow as well (clockwise to anticlockwise
            or anticlockwise to clockwise), so that the arrow remains on the same side
            of the component. Defaults to ``True``.
        """
        self.start, self.end = self.end, self.start
        if flip_sense_as_well:
            self.clockwise ^= True
        self.update()
        return self

    def __arrow_updater(self) -> None:
        self._direction = self.end.end - self.start.end
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
            angle = self._get_angle_from_middle_point(middle_point)
        else:
            angle = config_eng.symbol.voltage_default_angle

        direction = -1 if self.clockwise else 1

        # Remove once https://github.com/ManimCommunity/manim/issues/4132 is resolved
        # Manually calculates a buff so that a buff and path_arc don't occur
        # simultaneously
        start_to_end = self.end.end - self.start.end
        length = np.linalg.norm(start_to_end)
        radius = length / (2 * np.sin(0.5 * angle))
        angle_for_buff = self.buff / radius
        perp_bisector = np.cross(start_to_end, mn.IN) / length
        center = 0.5 * (self.start.end + self.end.end) + perp_bisector * np.sqrt(
            radius**2 - 0.25 * length**2
        )
        buffed_start = center + mn.rotate_vector(
            self.start.end - center, angle_for_buff * direction
        )
        buffed_end = center + mn.rotate_vector(
            self.end.end - center, angle_for_buff * -direction
        )
        path_arc = angle - 2 * angle_for_buff

        new_arrow = mn.Arrow(
            start=buffed_start,
            end=buffed_end,
            path_arc=path_arc * direction,
            stroke_width=config_eng.symbol.arrow_stroke_width,
            tip_length=config_eng.symbol.arrow_tip_length,
            # buff=self.buff, noqa: ERA001
            buff=0,
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
        direction = mn.normalize(relative_to_reference)
        length = np.linalg.norm(relative_to_reference)
        return relative_to + direction * (length + buff)

    def _get_angle_from_middle_point(self, middle_point: mnt.Point3D) -> float:
        """Calculate the voltage arrow's arc to pass through ``middle_point``.

        Calculates the necessary angle to be swept by the voltage arrow's arc for it to
        pass through ``middle_point`` as well as its endpoints defined by the
        ``start`` and ``end`` as passed to the constructor.

        In all cases two possible angles are available, one reflex and one not. This
        method will always return the non-reflex one. As such, avoid passing in points
        that require reflex angles.

        Parameters
        ----------
        middle_point : Point3D
            The extra point the arrow should pass through, as well as the two end points
            defined by the ``start`` and ``end`` terminals.

        Returns
        -------
        float
            The angle necessary for the arc to sweep to make the arrow pass through
            ``middle_point``.

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
        chord_ab = middle_point - self.start.end
        chord_bc = self.end.end - middle_point

        mid_ab = self.start.end + chord_ab / 2
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

    @mn.override_animate(set_label)
    def __animate_set_label(
        self,
        label: str,
        clockwise: bool | None = None,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        label_animation = (
            self.animate(**anim_args)._set_mark(self._label, label).build()
        )
        animations = [label_animation]

        if clockwise is not None:
            self._arrow.generate_target()
            self._arrow.target.set_clockwise(clockwise)
            arrow_animation = mn.MoveToTarget(self._arrow)
            animations.append(arrow_animation)

        return mn.AnimationGroup(*animations)

    @mn.override_animate(reset_label)
    def __animate_reset_label(
        self,
        label: str,
        clockwise: bool = False,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return (
            self.animate(**anim_args)
            .set_label(label=label, clockwise=clockwise)
            .build()
        )
