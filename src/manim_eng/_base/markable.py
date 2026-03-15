"""Contains the Markable base class.

See Also
--------
mark
"""

import abc
from typing import Any, Self

import manim as mn

from manim_eng._base.mark import Mark

__all__ = ["Markable"]


class RotateMarkable(mn.Rotate):
    """Override for the Rotate animation that keeps attached marks upright."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.current_rotation = 0.0

    def interpolate_mobject(self, alpha: float) -> None:
        target_angle = self.angle * alpha
        delta_angle = target_angle - self.current_rotation
        self.mobject.rotate(delta_angle, axis=self.axis, about_point=self.about_point)
        self.current_rotation += delta_angle


class Markable(mn.VMobject, metaclass=abc.ABCMeta):
    """Base class for objects that can have marks attached.

    Parameters
    ----------
    **kwargs : Any
        Keyword arguments to pass on to ``manim.VMobject``.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.__rotate = mn.VGroup()
        self.__marks = mn.VGroup()
        super().add(self.__rotate, self.__marks)

    def rotate(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Self:
        self.__rotate.rotate(*args, **kwargs)
        self.__reposition_marks()
        return self

    def add(self, *mobjects: mn.Mobject) -> Self:
        for mobject in mobjects:
            if isinstance(mobject, Markable):
                self.__rotate.add(mobject.__rotate)
                self.__marks.add(mobject.__marks)
            elif isinstance(mobject, Mark):
                self.__marks.add(mobject)
            else:
                self.__rotate.add(mobject)
        return self

    def add_to_back(self, *mobjects: mn.Mobject) -> Self:
        for mobject in mobjects:
            if isinstance(mobject, Markable):
                self.__rotate.add_to_back(mobject.__rotate)
                self.__marks.add_to_back(mobject.__marks)
            elif isinstance(mobject, Mark):
                self.__marks.add_to_back(mobject)
            else:
                self.__rotate.add_to_back(mobject)
        return self

    def remove(self, *mobjects: mn.Mobject) -> Self:
        for mobject in mobjects:
            if isinstance(mobject, Markable):
                self.__rotate.remove(mobject.__rotate)
                self.__marks.remove(mobject.__marks)
            elif isinstance(mobject, Mark):
                self.__marks.remove(mobject)
            else:
                self.__rotate.remove(mobject)
        return self

    def __reposition_marks(self) -> None:
        """Force marks to update their positions even if updating is disabled."""
        for mark in self.__marks.submobjects:
            mark._reposition()

    @mn.override_animation(mn.Rotate)
    def __animate_rotate(self, **kwargs: Any) -> mn.Animation:
        return RotateMarkable(self, **kwargs)
