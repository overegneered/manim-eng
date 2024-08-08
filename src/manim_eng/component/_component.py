import abc
from dataclasses import dataclass
from typing import Any, Self

import manim as mn
import manim.typing as mnt
import numpy as np
import numpy.typing as npt

from .._debug.anchor import (
    ANNOTATION_COLOUR,
    CENTRE_COLOUR,
    LABEL_COLOUR,
    TERMINAL_COLOUR,
    Anchor,
)

MARK_FONT_SIZE = 36


@dataclass
class Terminal:
    position: npt.NDArray[np.float64]
    direction: npt.NDArray[np.float64]


class Component(mn.VMobject, metaclass=abc.ABCMeta):
    """Base class for a circuit symbol.

    Parameters
    ----------
    label : str | None
        A label to set. Takes a TeX math mode string. No label is set if ``None`` is
        passed.
    annotation : str | None
        An annotation to set. Takes a TeX math mode string. No annotation is set if
        ``None`` is passed.
    debug : bool
        Whether to display debug information for the component. If ``True``, the
        component's anchors will be displayed visually.
    """

    def __init__(
        self,
        label: str | None = None,
        annotation: str | None = None,
        debug: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self._terminals: list[Terminal] = []
        self._label: mn.MathTex | None = None
        self._annotation: mn.MathTex | None = None
        self._centre_anchor: Anchor
        self._label_anchor: Anchor
        self._annotation_anchor: Anchor

        self._body = mn.VGroup()
        self._anchors = mn.VGroup()
        self._marks = mn.VGroup()
        self._rotate = mn.VGroup(self._body, self._anchors)
        self.add(self._rotate, self._marks)

        self._construct()
        self.__set_up_anchors(debug)
        self.__set_up_marks(annotation, label)

    @abc.abstractmethod
    def _construct(self) -> None:
        """Construct the shape of the component.

        Code to build the component's symbol goes in here (contrary to Manim's
        standard) and *not* ``__init__()``. This is because the base ``Component`` class
        has to perform initialisation both before (to set up the groups etc.) and after
        (to set the anchor positions for annotations) the component's shape setup.
        """

    def get_center(self) -> mnt.Point3D:
        """Get the centre of the component.

        **This is not necessarily the exact centre of the box the component symbol
        occupies**. It is rather the point about which it is most logical to rotate
        the component. For bipoles, it will be at the midpoint of the line between the
        two terminals.

        Returns
        -------
        Point3D
            The centre of the component.
        """
        return self._centre_anchor.get_center()

    def rotate(
        self,
        angle: float = mn.PI,
        about_point: mnt.Point3D | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> Self:
        self._rotate.rotate(*args, angle=angle, about_point=about_point, **kwargs)
        return self

    def set_label(self, label: str) -> Self:
        """Set the label of the component.

        Parameters
        ----------
        label : str
            The label to set. Takes a TeX math mode string.

        Returns
        -------
        Self
            The (modified) component on which the method was called.
        """
        self._label = self._replace_mark(self._label, label, self._label_anchor)
        return self

    def clear_label(self) -> Self:
        """Clear the label of the component.

        Returns
        -------
        Self
            The (modified) component on which the method was called.
        """
        if self._label is not None:
            self._marks.remove(self._label)
        self._label = None
        return self

    def set_annotation(self, annotation: str) -> Self:
        """Set the annotation of the component.

        Parameters
        ----------
        annotation : str
            The annotation to set. Takes a TeX math mode string.

        Returns
        -------
        Self
            The (modified) component on which the method was called.
        """
        self._annotation = self._replace_mark(
            self._annotation, annotation, self._annotation_anchor
        )
        return self

    def clear_annotation(self) -> Self:
        """Clear the annotation of the component.

        Returns
        -------
        Self
            The (modified) component on which the method was called
        """
        if self._annotation is not None:
            self._marks.remove(self._annotation)
        self._annotation = None
        return self

    def __set_up_anchors(self, debug: bool) -> None:
        self._centre_anchor = Anchor(debug, CENTRE_COLOUR)
        self._label_anchor = Anchor(debug, LABEL_COLOUR).shift(
            self._body.get_top() + 0.4 * mn.UP
        )
        self._annotation_anchor = Anchor(debug, ANNOTATION_COLOUR).shift(
            self._body.get_bottom() + 0.4 * mn.DOWN
        )
        self._anchors.add(
            self._centre_anchor, self._label_anchor, self._annotation_anchor
        )
        for terminal in self._terminals:
            self._anchors.add(Anchor(debug, TERMINAL_COLOUR).shift(terminal.position))

    def __set_up_marks(self, annotation: str | None, label: str | None) -> None:
        if label is not None:
            self.set_label(label)
        if annotation is not None:
            self.set_annotation(annotation)

    def _replace_mark(
        self, old_mark: mn.MathTex, mark_text: str, anchor: Anchor
    ) -> mn.MathTex:
        """Replace a mark with a new mark, and return that new mark.

        Parameters
        ----------
        old_mark : MathTex
            The mark to replace.
        mark_text : str
            The text to use for the new mark. Takes a TeX math mode
            string.
        anchor : Anchor
            The anchor to affix the mark to.

        Returns
        -------
        MathTex
            The new mark.
        """

        def mark_updater(mark: mn.Mobject) -> None:
            mark.move_to(anchor)

        new_mark = mn.MathTex(mark_text, font_size=MARK_FONT_SIZE).move_to(anchor)
        new_mark.add_updater(mark_updater)
        if old_mark is not None:
            self._marks.remove(old_mark)
        self._marks.add(new_mark)
        return new_mark

    @mn.override_animate(set_label)
    def _animate_set_label(
        self,
        *set_label_args: Any,
        anim_args: dict[str, Any] | None = None,
        **set_label_kwargs: Any,
    ) -> mn.Animation:
        old_label = self._label
        self.set_label(*set_label_args, **set_label_kwargs)
        return self._animate_set_mark(old_label, self._label, anim_args)

    @mn.override_animate(clear_label)
    def _animate_clear_label(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        anim = self._animate_clear_mark(self._label, anim_args)
        self.clear_label()
        return anim

    @mn.override_animate(set_annotation)
    def _animate_set_annotation(
        self,
        *set_annotation_args: Any,
        anim_args: dict[str, Any] | None = None,
        **set_annotation_kwargs: Any,
    ) -> mn.Animation:
        old_annotation = self._annotation
        self.set_annotation(*set_annotation_args, **set_annotation_kwargs)
        return self._animate_set_mark(old_annotation, self._annotation, anim_args)

    @mn.override_animate(clear_annotation)
    def _animate_clear_annotation(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        anim = self._animate_clear_mark(self._annotation, anim_args)
        self.clear_annotation()
        return anim

    @staticmethod
    def _animate_set_mark(
        old_mark: mn.MathTex | None,
        new_mark: mn.MathTex,
        anim_args: dict[str, Any] | None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        if old_mark is None:
            return mn.Create(new_mark, **anim_args)

        return mn.AnimationGroup(
            mn.FadeOut(old_mark, shift=mn.DOWN, **anim_args),
            mn.FadeIn(new_mark, shift=mn.DOWN, **anim_args),
        )

    @staticmethod
    def _animate_clear_mark(
        old_mark: mn.MathTex, anim_args: dict[str, Any] | None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return mn.Uncreate(old_mark, **anim_args)


class Bipole(Component, metaclass=abc.ABCMeta):
    """Base class for bipole components, such as resistors and sources."""

    def __init__(
        self,
        left: Terminal | None = None,
        right: Terminal | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.left = left or Terminal(position=mn.LEFT, direction=mn.RIGHT)
        self.right = right or Terminal(position=mn.RIGHT, direction=mn.LEFT)
        super().__init__(*args, **kwargs)

    def _construct(self) -> None:
        self._terminals = [self.left, self.right]
