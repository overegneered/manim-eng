"""Contains CurrentArrow class for drawing current arrows on lines."""

from typing import Self

import manim as mn
from manim import typing as mnt

from manim_eng import config_eng
from manim_eng._base import Mark, Markable
from manim_eng._base.anchor import AnnotationAnchor, CentreAnchor, LabelAnchor

__all__ = ["CurrentArrow"]


class CurrentArrow(Markable):
    """Current arrow placed along a line.

    Parameters
    ----------
    parent : manim.VMobject
        The mobject to place the arrow on.
    alpha : float, optional
        How far along ``parent`` the arrow should be placed, with ``alpha = 0`` being at
        the start and ``alpha = 1`` at the end. Default is ``0.5`` (i.e. the middle).
    invert : bool, optional
        If set, ``alpha`` measures from the end to the start, and the arrow will point
        accordinly. Default is ``False``.
    label : str, optional
        Initial current label to set, if desired. Placed anticlockwise from the tip.
    annotation : str, optional
        Initial current annotation to set, if desired. Placed clockwise from the tip.
    """

    def __init__(
        self,
        parent: mn.VMobject,
        alpha: float = 0.5,
        invert: bool = False,
        label: str | None = None,
        annotation: str | None = None,
    ) -> None:
        super().__init__()

        self._parent = parent
        self._alpha = alpha
        self._invert = invert

        self._triangle = mn.Triangle(
            radius=config_eng.symbol.current_arrow_radius,
            start_angle=0,
            color=mn.WHITE,
            fill_opacity=1.0,
        )

        self._label_anchor = LabelAnchor().move_to(self._triangle.get_top())
        self._annotation_anchor = AnnotationAnchor().move_to(
            self._triangle.get_bottom()
        )
        self._centre_anchor = CentreAnchor().move_to(
            (self._label_anchor.pos + self._annotation_anchor.pos) / 2
        )

        self.label = Mark(self._label_anchor, self._centre_anchor, label)
        self.annotation = Mark(self._annotation_anchor, self._centre_anchor, annotation)

        self.add(
            self._triangle,
            self._centre_anchor,
            self._label_anchor,
            self._annotation_anchor,
            self.label,
            self.annotation,
        )
        self.__reposition()
        self.add_updater(lambda mob: mob.__reposition())

    def set(self, label: str) -> Self:
        """Set the label for the current arrow.

        Shorthand for `.label.set()`
        """
        self.label.set(label)
        return self

    def __reposition(self) -> None:
        new_pos, new_angle = self.__calculate_new_pose()
        self.shift(new_pos - self._centre_anchor.pos)
        self.rotate(new_angle - self.__current_angle())

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
