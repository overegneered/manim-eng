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

    Notes
    -----
    Internally replaces `submobjects` with three groups:

    - ``__rotate``, which contains most mobjects
    - ``__marks``, which contains :class:`~.Mark`s
    - ``__markables``, which contains child :class:`~.Markable`s

    Through these, marks can be kept upright when attached to markables.
    """

    def __init__(self, **kwargs: Any) -> None:
        # Because of the override on self.submobjects, we don't need to add these
        # directly — the override presents them
        self.__rotate = mn.VGroup()
        self.__marks = mn.VGroup()
        self.__markables = mn.VGroup()

        super().__init__(**kwargs)

    def rotate(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Self:
        """Rotates the :class:`~.Markable` object about a certain point.

        Only non-marks will be rotated.

        Parameters
        ----------
        *args : Any
            Positional arguments to pass on to :meth:`~.Mobject.rotate`.
        **kwargs : Any
            Keyword arguments to pass on to :meth:`~.Mobject.rotate`.
        """
        self.__rotate.rotate(*args, **kwargs)
        for markable in self.__markables:
            markable.rotate(*args, **kwargs)
        self._reposition_marks()
        return self

    def add(self, *mobjects: mn.Mobject) -> Self:
        for mobject in mobjects:
            if isinstance(mobject, Markable):
                self.__markables.add(mobject)
            elif isinstance(mobject, Mark):
                self.__marks.add(mobject)
            else:
                self.__rotate.add(mobject)
        return self

    def add_to_back(self, *mobjects: mn.Mobject) -> Self:
        for mobject in mobjects:
            if isinstance(mobject, Markable):
                self.__markables.add_to_back(mobject)
            elif isinstance(mobject, Mark):
                self.__marks.add_to_back(mobject)
            else:
                self.__rotate.add_to_back(mobject)
        return self

    def remove(self, *mobjects: mn.Mobject) -> Self:
        for mobject in mobjects:
            if isinstance(mobject, Markable):
                self.__markables.remove(mobject)
            elif isinstance(mobject, Mark):
                self.__marks.remove(mobject)
            else:
                self.__rotate.remove(mobject)
        return self

    @property
    def submobjects(self) -> list[mn.VMobject]:
        """The submobjects associated with this object.

        Notes
        -----
        This is an abstraction over the more complicated internal representation used by
        :class:`~.Markable`. The returned mobjects will always be in this order:

        1. Direct children that rotate;
        2. Direct children that are marks;
        3. Child :class:`~.Markable` instances.

        There is however no way to get the boundary indices between these groups.
        """
        to_return: list[mn.VMobject] = (
            self.__rotate.submobjects
            + self.__marks.submobjects
            + self.__markables.submobjects
        )
        return to_return

    @submobjects.setter
    def submobjects(self, value: list[mn.VMobject]) -> None:
        self.__rotate.submobjects = []
        self.__marks.submobjects = []
        self.__markables.submobjects = []
        self.add(*value)

    def _reposition_marks(self) -> None:
        """Force marks to update their positions even if updating is disabled."""
        for mark in self.__marks.submobjects:
            mark._reposition()
        for markable in self.__markables.submobjects:
            markable._reposition_marks()

    @mn.override_animation(mn.Rotate)
    def __animate_rotate(self, **kwargs: Any) -> mn.Animation:
        return RotateMarkable(self, **kwargs)
