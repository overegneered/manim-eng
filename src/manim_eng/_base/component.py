import abc
from typing import Any, Self

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng._base.mark import Mark, Markable
from manim_eng._base.terminal import Terminal
from manim_eng._config import config_eng
from manim_eng._debug.anchor import Anchor


class Component(Markable, metaclass=abc.ABCMeta):
    """Base class for a circuit symbol.

    Parameters
    ----------
    terminals : list[Terminal]
        The terminals of the component. Management of terminal visibility is handled by
        the constructor; terminals should not be added before or after they are passed
        to this constructor.
    label : str | None
        A label to set. Takes a TeX math mode string. No label is set if ``None`` is
        passed.
    annotation : str | None
        An annotation to set. Takes a TeX math mode string. No annotation is set if
        ``None`` is passed.
    """

    def __init__(
        self,
        terminals: list[Terminal],
        label: str | None = None,
        annotation: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self._terminals = terminals
        self.add(*self._terminals)

        self._centre_anchor: Anchor
        self._label_anchor: Anchor
        self._annotation_anchor: Anchor

        self._body = mn.VGroup()
        self.add(self._body)

        self._construct()

        self.__set_up_anchors()
        self._label = Mark(self._label_anchor, self._centre_anchor)
        self._annotation = Mark(self._annotation_anchor, self._centre_anchor)
        self.__initialise_marks(label, annotation)

    @abc.abstractmethod
    def _construct(self) -> None:
        """Construct the shape of the component.

        Code to build the component's symbol goes in here (contrary to Manim's
        standard) and *not* ``__init__()``. This is because the base ``Component`` class
        has to perform initialisation both before (to set up the groups etc.) and after
        (to set the anchor positions for annotations) the component's shape setup.
        """

    def get_center(self) -> mnt.Point3D:
        """Get the centre of the components.

        **This is not necessarily the exact centre of the box the component symbol
        occupies**. It is rather the point about which it is most logical to rotate
        the component. For bipoles, it will be at the midpoint of the line between the
        two terminals.

        Returns
        -------
        Point3D
            The centre of the components.
        """
        return self._centre_anchor.get_center()

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
        self._set_mark(self._label, label)
        return self

    def clear_label(self) -> Self:
        """Clear the label of the component.

        Returns
        -------
        Self
            The (modified) component on which the method was called.
        """
        self._clear_mark(self._label)
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
        self._set_mark(self._annotation, annotation)
        return self

    def clear_annotation(self) -> Self:
        """Clear the annotation of the component.

        Returns
        -------
        Self
            The (modified) component on which the method was called
        """
        self._clear_mark(self._annotation)
        return self

    def __set_up_anchors(self) -> None:
        self._centre_anchor = Anchor(config_eng.anchor.centre_colour)
        # A small amount is added to each of these anchors to make sure that they are
        # never directly over the centre anchor, as this causes problems.
        self._label_anchor = Anchor(config_eng.anchor.label_colour).shift(
            self._body.get_top() + 0.01 * mn.UP
        )
        self._annotation_anchor = Anchor(config_eng.anchor.annotation_colour).shift(
            self._body.get_bottom() + 0.01 * mn.DOWN
        )
        self.add(self._centre_anchor, self._label_anchor, self._annotation_anchor)

    def __initialise_marks(self, label: str | None, annotation: str | None) -> None:
        if label is not None:
            self.set_label(label)
        if annotation is not None:
            self.set_annotation(annotation)

    @mn.override_animate(set_label)
    def _animate_set_label(
        self, label: str, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return self.animate(**anim_args)._set_mark(self._label, label).build()

    @mn.override_animate(clear_label)
    def _animate_clear_label(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return self.animate(**anim_args)._clear_mark(self._label).build()

    @mn.override_animate(set_annotation)
    def _animate_set_annotation(
        self, label: str, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return self.animate(**anim_args)._set_mark(self._annotation, label).build()

    @mn.override_animate(clear_annotation)
    def _animate_clear_annotation(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return self.animate(**anim_args)._clear_mark(self._annotation).build()


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
    debug : bool
        Whether to display debug information. If ``True``, the object's anchors will be
        displayed visually.
    """

    def __init__(
        self,
        left: Terminal | None = None,
        right: Terminal | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        terminal_end_x = (
            config_eng.symbol.bipole_width / 2
        ) + config_eng.symbol.terminal_length
        terminal_end = np.array([terminal_end_x, 0, 0])

        left = (
            left
            if left is not None
            else Terminal(position=-terminal_end, direction=mn.LEFT)
        )
        right = (
            right
            if right is not None
            else Terminal(position=terminal_end, direction=mn.RIGHT)
        )
        super().__init__([left, right], *args, **kwargs)

    @property
    def left(self) -> Terminal:
        return self._terminals[0]

    @property
    def right(self) -> Terminal:
        return self._terminals[1]
