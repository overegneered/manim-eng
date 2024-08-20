import abc
from typing import Any, Self

import manim as mn
import manim.typing as mnt
import numpy as np

import manim_eng._utils as utils
from manim_eng._debug.anchor import (
    ANNOTATION_COLOUR,
    CENTRE_COLOUR,
    LABEL_COLOUR,
    TERMINAL_COLOUR,
    Anchor,
)

from .._component import MARK_FONT_SIZE
from .._component.terminal import Terminal

# How many radians off a cardinal direction of alignment a components can be whilst the
# mark alignments still treat it as in a cardinal alignment
CARDINAL_ALIGNMENT_MARGIN = 5 * (np.pi / 180)


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
        Whether to display debug information for the components. If ``True``, the
        components's anchors will be displayed visually.
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

        self._label: mn.MathTex | None = None
        self._annotation: mn.MathTex | None = None
        self._centre_anchor: Anchor
        self._label_anchor: Anchor
        self._annotation_anchor: Anchor

        self._terminals = mn.VGroup()
        self._body = mn.VGroup(self._terminals)
        self._anchors = mn.VGroup()
        self._rotate = mn.VGroup(self._body, self._anchors)
        self._marks = mn.VGroup()
        self.add(self._rotate, self._marks)

        self._construct()
        self.__set_up_anchors(debug)
        self.__set_up_marks(annotation, label)

    @abc.abstractmethod
    def _construct(self) -> None:
        """Construct the shape of the components.

        Code to build the components's symbol goes in here (contrary to Manim's
        standard) and *not* ``__init__()``. This is because the base ``Component`` class
        has to perform initialisation both before (to set up the groups etc.) and after
        (to set the anchor positions for annotations) the components's shape setup.
        """

    def get_center(self) -> mnt.Point3D:
        """Get the centre of the components.

        **This is not necessarily the exact centre of the box the components symbol
        occupies**. It is rather the point about which it is most logical to rotate
        the components. For bipoles, it will be at the midpoint of the line between the
        two terminals.

        Returns
        -------
        Point3D
            The centre of the components.
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
        self._marks.update()
        return self

    def set_label(self, label: str) -> Self:
        """Set the label of the components.

        Parameters
        ----------
        label : str
            The label to set. Takes a TeX math mode string.

        Returns
        -------
        Self
            The (modified) components on which the method was called.
        """
        self._label = self._replace_mark(self._label, label, self._label_anchor)
        return self

    def clear_label(self) -> Self:
        """Clear the label of the components.

        Returns
        -------
        Self
            The (modified) components on which the method was called.
        """
        if self._label is not None:
            self._marks.remove(self._label)
        self._label = None
        return self

    def set_annotation(self, annotation: str) -> Self:
        """Set the annotation of the components.

        Parameters
        ----------
        annotation : str
            The annotation to set. Takes a TeX math mode string.

        Returns
        -------
        Self
            The (modified) components on which the method was called.
        """
        self._annotation = self._replace_mark(
            self._annotation, annotation, self._annotation_anchor
        )
        return self

    def clear_annotation(self) -> Self:
        """Clear the annotation of the components.

        Returns
        -------
        Self
            The (modified) components on which the method was called
        """
        if self._annotation is not None:
            self._marks.remove(self._annotation)
        self._annotation = None
        return self

    def __set_up_anchors(self, debug: bool) -> None:
        self._centre_anchor = Anchor(debug, CENTRE_COLOUR)
        # A small amount is added to each of these anchors to make sure that they are
        # never directly over the centre anchor, as this causes problems.
        self._label_anchor = Anchor(debug, LABEL_COLOUR).shift(
            self._body.get_top() + 0.01 * mn.UP
        )
        self._annotation_anchor = Anchor(debug, ANNOTATION_COLOUR).shift(
            self._body.get_bottom() + 0.01 * mn.DOWN
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
            line_of_connection = anchor.pos - self._centre_anchor.pos
            line_of_connection = utils.normalised(line_of_connection)
            line_of_connection = utils.cardinalised(
                line_of_connection, CARDINAL_ALIGNMENT_MARGIN
            )
            mark.next_to(
                mobject_or_point=anchor.pos,
                direction=line_of_connection,
                buff=mn.SMALL_BUFF,
            )

        new_mark = mn.MathTex(mark_text, font_size=MARK_FONT_SIZE)
        new_mark.add_updater(mark_updater)
        new_mark.update()
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
    """Base class for bipole components, such as resistors and sources.

    By default, adds two terminals: one from (-0.5, 0) to (-1, 0), and one from (0.5, 0)
    to (1, 0).

    Parameters
    ----------
    left : Terminal | None
        The terminal to use as the left connection point for the component. If left
        unspecified, a terminal from (-0.5, 0) to (-1, 0) will be used.
    right : Terminal | None
        The terminal to use as the right connection point for the component. If left
        unspecified, a terminal from (-0.5, 0) to (-1, 0) will be used.
    """

    def __init__(
        self,
        left: Terminal | None = None,
        right: Terminal | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.left = (
            left if left is not None else Terminal(position=mn.LEFT, direction=mn.LEFT)
        )
        self.right = (
            right
            if right is not None
            else Terminal(position=mn.RIGHT, direction=mn.RIGHT)
        )
        super().__init__(*args, **kwargs)

    def _construct(self) -> None:
        self._terminals.add(self.left, self.right)
