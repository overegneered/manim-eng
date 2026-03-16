"""Contains CurrentArrow class for drawing current arrows on lines."""

from typing import Any, Self

import manim as mn
from manim import typing as mnt

from manim_eng import config_eng
from manim_eng._base import Mark, Markable
from manim_eng._base.anchor import CentreAnchor, LabelAnchor

__all__ = ["CurrentArrow"]


class CurrentArrow(Markable):
    """Current arrow placed along a line.

    Parameters
    ----------
    parent : manim.VMobject
        The mobject to place the arrow on.
    label : str, optional
        Initial current label to set, if desired. Placed anticlockwise from the tip.
    alpha : float, optional
        How far along ``parent`` the arrow should be placed, with ``alpha = 0`` being at
        the start and ``alpha = 1`` at the end. Default is ``0.5`` (i.e. the middle).
    invert : bool, optional
        If set, ``alpha`` measures from the end to the start, and the arrow will point
        accordinly. Default is ``False``.
    """

    def __init__(
        self,
        parent: mn.VMobject,
        label: str | None = None,
        alpha: float = 0.5,
        invert: bool = False,
    ) -> None:
        super().__init__()

        self._parent = parent
        self._alpha = alpha
        self._invert = invert

        self._centre_anchor = CentreAnchor()
        self._triangle = self.__build_triangle(angle=0)
        self._label_anchor = LabelAnchor().move_to(self._triangle.get_top())

        self._label = Mark(self._label_anchor, self._centre_anchor, label)

        self.add(
            self._centre_anchor,
            self._label_anchor,
            self._label,
        )
        if label is not None:
            self.add(self._triangle)

        self.__reposition()
        self.add_updater(lambda mob: mob.__reposition())

    def set(
        self,
        label: str | None = None,
        alpha: float | None = None,
        invert: bool | None = None,
    ) -> Self:
        """Set aspects of the current arrow.

        Any parameters left unspecified will be left unchanged.

        Parameters
        ----------
        label : str, optional
            Current label to set. Placed anticlockwise from the tip.
        alpha : float, optional
            How far along ``parent`` the arrow should be placed, with ``alpha = 0``
            being at the start and ``alpha = 1`` at the end.
        invert : bool, optional
            If set, ``alpha`` measures from the end to the start, and the arrow will
            point accordingly.
        """
        if label is not None:
            self._label.set(label)
            if self._triangle not in self.submobjects:
                self._triangle = self.__build_triangle()
                self.add(self._triangle)
        if alpha is not None:
            self._alpha = alpha
        if invert is not None:
            self._invert = invert
        return self

    @mn.override_animate(set)
    def __animate_set(
        self,
        label: str | None = None,
        alpha: float | None = None,
        invert: bool | None = None,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation | None:
        if anim_args is None:
            anim_args = {}

        if self._triangle in self.submobjects:
            if alpha is not None or invert is not None:
                self.generate_target()
                if alpha is not None:
                    self.target._alpha = alpha
                if invert is not None:
                    self.target._invert = invert
                if label is not None:
                    self.target._label.set(label)
                return mn.MoveToTarget(self, **anim_args)
            if label is not None:
                return self._label.animate(**anim_args).set(label).build()
            return None

        animations = []

        if alpha is not None:
            self._alpha = alpha
        if invert is not None:
            self._invert = invert
        self.__reposition()

        self._triangle = self.__build_triangle()
        animations.append(mn.Create(self._triangle, **anim_args))
        self.add(self._triangle)

        if label is not None:
            animations.append(self._label.animate(**anim_args).set(label).build())

        return mn.AnimationGroup(*animations)

    def clear(self) -> Self:
        """Clear the current arrow.

        This will remove both the arrow and current label.
        """
        self.remove(self._triangle)
        self._label.clear()
        return self

    def flip_direction(self) -> Self:
        """Flip the direction of the current arrow.

        Flips the direction of the current arrow while adjusting ``alpha`` to avoid it
        jumping about.
        """
        self._alpha = 1 - self._alpha
        self._invert = not self._invert
        return self

    def __reposition(self) -> None:
        new_pos, new_angle = self.__calculate_new_pose()
        self.shift(new_pos - self._centre_anchor.pos)
        angle_delta = new_angle - self.__current_angle()
        self.rotate(angle_delta)

    def __calculate_new_pose(self) -> tuple[mnt.Point3D, float]:
        epsilon = 1e-6
        alpha = self._alpha

        if self._invert:
            alpha = 1 - alpha
            epsilon *= -1

        centre = self._parent.point_from_proportion(alpha)
        forward = self._parent.point_from_proportion(alpha + epsilon)
        angle = mn.angle_of_vector(forward - centre)
        return centre, angle

    def __current_angle(self) -> float:
        up = self._label_anchor.pos - self._centre_anchor.pos
        # Mypy can't work out that this is of type float
        return mn.angle_of_vector(up) - mn.PI / 2.0  # type: ignore[no-any-return]

    def __build_triangle(self, angle: float | None = None) -> mn.Triangle:
        if angle is None:
            angle = self.__current_angle()
        return mn.Triangle(
            radius=config_eng.symbol.current_arrow_radius,
            start_angle=angle,
            color=mn.WHITE,
            fill_opacity=1.0,
        ).move_to(self._centre_anchor.pos)
