import abc
from typing import Any, Self

import manim as mn

import manim_eng._utils as utils
from manim_eng._config import config_eng

from ..._debug.anchor import Anchor


class AlreadyAttachedError(RuntimeError):
    pass


class Mark(mn.VMobject):
    """A mark object, representing any textual annotation on a component.

    Parameters
    ----------
    anchor : Anchor
        The anchor to use as a base for the attachment of the mark.
    centre_reference : Anchor
        The anchor to use as a reference; the mark will be kept aligned to ``anchor``,
        attached to the side directly opposite the side ``centre_reference`` is on.
    """

    def __init__(self, anchor: Anchor, centre_reference: Anchor) -> None:
        super().__init__()
        self.mathtex: mn.MathTex | None = None

        if (anchor.pos == centre_reference.pos).all():
            raise ValueError(
                "`anchor` and `centre_reference` cannot be the same. "
                f"Found: {anchor=}, {centre_reference=}.\n"
                "Please report this error to a developer."
            )

        def updater(mark: mn.Mobject) -> None:
            line_of_connection = anchor.pos - centre_reference.pos
            line_of_connection = utils.normalised(line_of_connection)
            line_of_connection = utils.cardinalised(
                line_of_connection, config_eng.symbol.mark_cardinal_alignment_margin
            )
            mark.next_to(
                mobject_or_point=anchor.pos,
                direction=line_of_connection,
                buff=mn.SMALL_BUFF,
            )

        self.add_updater(updater)
        self.update()

    def set_text(
        self,
        *args: Any,
        font_size: float = config_eng.symbol.mark_font_size,
        **kwargs: Any,
    ) -> Self:
        """Set the text of the mark.

        Parameters
        ----------
        *args : Any
            Positional arguments to be pass on to ``manim.MathTex``. The most important
            of these is ``*tex_strings``, i.e. the actual TeX math mode strings to use
            as the mark's text.
        font_size : float
            The font size to use for the mark. Leaving it empty adopts the default
            (recommended).
        **kwargs : Any
            Keyword arguments to pass on to ``manim.MathTex``.
        """
        if self.mathtex is not None:
            self.remove(self.mathtex)
        self.mathtex = mn.MathTex(*args, font_size=font_size, **kwargs)
        self.add(self.mathtex)
        self.update()
        return self

    @property
    def tex_strings(self) -> list[str] | None:
        if self.mathtex is None:
            return None
        return self.mathtex.tex_strings  # type: ignore[no-any-return]


class Markable(mn.VMobject, metaclass=abc.ABCMeta):
    """Base class for objects that can have marks attached.

    Parameters
    ----------
    *args : Any
        Positional arguments to pass on to ``manim.VMobject``.
    **kwargs : Any
        Keyword arguments to pass on to ``manim.VMobject``.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

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
        anim = mn.Uncreate(mark_to_clear, **anim_args)
        self.__marks.remove(mark_to_clear)
        return anim
