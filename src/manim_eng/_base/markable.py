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
        return self

    def add(self, *mobjects: mn.Mobject) -> Self:
        for mobject in [*mobjects]:
            if isinstance(mobject, Markable):
                self.__rotate.add(mobject.__rotate)
                self.__marks.add(mobject.__marks)
            else:
                self.__rotate.add(*mobjects)
        return self

    def add_to_back(self, *mobjects: mn.Mobject) -> Self:
        for mobject in [*mobjects]:
            if isinstance(mobject, Markable):
                self.__rotate.add_to_back(mobject.__rotate)
                self.__marks.add_to_back(mobject.__marks)
            else:
                self.__rotate.add_to_back(*mobjects)
        return self

    def remove(self, *mobjects: mn.Mobject) -> Self:
        for mobject in [*mobjects]:
            if isinstance(mobject, Markable):
                self.__rotate.remove(mobject.__rotate)
                self.__marks.remove(mobject.__marks)
            else:
                self.__rotate.remove(*mobjects)
        return self

    def _set_mark(self, mark_to_set: Mark, mark_text: str) -> None:
        """Set a mark's label, adding the mark if necessary."""
        if mark_to_set not in self.__marks.submobjects:
            self.__marks.add(mark_to_set)
        mark_to_set.set_text(mark_text)

    def _clear_mark(self, mark: Mark) -> None:
        """Clear a mark from the object."""
        if mark in self.__marks.submobjects:
            self.__marks.remove(mark)

    @mn.override_animate(_set_mark)
    def __animate_set_mark(
        self, mark_to_set: Mark, mark_text: str, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        if mark_to_set not in self.__marks.submobjects:
            self.__marks.add(mark_to_set)
            return mn.Create(mark_to_set.set_text(mark_text))

        mark_to_set.generate_target()
        mark_to_set.target.set_text(mark_text)
        return mn.MoveToTarget(mark_to_set, **anim_args)

    @mn.override_animate(_clear_mark)
    def __animate_clear_mark(
        self, mark_to_clear: Mark, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        anim = mn.Uncreate(mark_to_clear, remover=False, **anim_args)
        self.__marks.remove(mark_to_clear)
        return anim
