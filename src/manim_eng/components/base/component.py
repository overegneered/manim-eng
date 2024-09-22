"""Module containing the Component base class."""

import abc
from typing import Any, Self

import manim as mn
import manim.typing as mnt

from manim_eng._base.mark import Mark
from manim_eng._base.markable import Markable
from manim_eng._debug.anchor import AnnotationAnchor, CentreAnchor, LabelAnchor
from manim_eng.circuit.voltage import Voltage
from manim_eng.components.base.terminal import Terminal

__all__ = ["Component"]


class Component(Markable, metaclass=abc.ABCMeta):
    """Base class for all components.

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

        self.terminals = terminals

        self._centre_anchor = CentreAnchor()
        self._label_anchor = LabelAnchor()
        self._annotation_anchor = AnnotationAnchor()

        self._body = mn.VGroup(*self.terminals)
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
            The (modified) component on which the method was called.
        """
        self._clear_mark(self._annotation)
        return self

    def voltage(
        self,
        from_terminal: Terminal | str,
        to_terminal: Terminal | str,
        *args: Any,
        **kwargs: Any,
    ) -> Voltage:
        """Return a voltage arrow across the component.

        Convenience method for creating a voltage arrow across two terminals of this
        component. Returns the created ``Voltage`` object. This method automatically
        sets the component is it called upon in the ``avoid`` argument of ``Voltage``
        (and as such overrides this argument).

        Parameters
        ----------
        from_terminal : Terminal | str
            Either a ``Terminal`` belonging to this component, or a string representing
            an attribute of this component that returns a terminal (e.g. ``"right"``).
        to_terminal : Terminal | str
            Either a ``Terminal`` belonging to this component, or a string representing
            an attribute of this component that returns a terminal (e.g. ``"left"``).
        *args
            Positional arguments to be passed to the ``Voltage`` constructor.
        **kwargs
            Keyword arguments to be passed to the ``Voltage`` constructor. Any keyword
            argument with the key ``avoid`` will be ignored.

        Returns
        -------
        Voltage
            The voltage arrow resulting from the specification given.

        Raises
        ------
        ValueError
            If a passed ``Terminal`` does not belong to this component.
        AttributeError
            If a string passed for either terminal does not represent an existing
            attribute.
        ValueError
            If a string passed for either terminal does not represent an attribute of
            this component that produces a ``Terminal`` instance.
        ValueError
            If the terminals specified for both 'from' and 'to' are the same.
        """
        from_terminal = self._get_or_check_terminal(from_terminal)
        to_terminal = self._get_or_check_terminal(to_terminal)

        if from_terminal == to_terminal:
            raise ValueError(
                "The terminals specified through `from_terminal` and `to_terminal` are "
                "identical. They must be different."
            )

        kwargs["avoid"] = self

        return Voltage(from_terminal, to_terminal, *args, **kwargs)

    def _get_or_check_terminal(self, terminal: Terminal | str) -> Terminal:
        """Get a terminal or check a passed terminal belongs to this component.

        Parameters
        ----------
        terminal : Terminal | str
            The string to use as a terminal identifier, or a ``Terminal`` instance to
            verify belongs to this component.

        Returns
        -------
        Terminal
            The terminal identified.

        Raises
        ------
        AttributeError
            If the string passed for the terminal doesn't exist as an attribute on this
            component.
        ValueError
            If the attribute identified by the string isn't an instance of ``Terminal``.
        ValueError
            If the terminal passed doesn't belong to this component.
        """
        if isinstance(terminal, Terminal):
            if terminal not in self.terminals:
                raise ValueError("Passed terminal does not belong to this component.")
            to_return = terminal
        else:
            to_return = getattr(self, terminal)
            if not isinstance(to_return, Terminal):
                raise ValueError(
                    f"Attribute `{terminal}` of `{self.__class__.__name__}` "
                    f"is not a terminal."
                )
        return to_return

    def __set_up_anchors(self) -> None:
        # A small amount is added to each of these anchors to make sure that they are
        # never directly over the centre anchor, as this causes problems.
        self._label_anchor.shift(self._body.get_top() + 0.01 * mn.UP)
        self._annotation_anchor.shift(self._body.get_bottom() + 0.01 * mn.DOWN)
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
