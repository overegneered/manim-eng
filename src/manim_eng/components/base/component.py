"""Contains the Component base class."""

import abc
from typing import Any, Self

import manim as mn
import manim.typing as mnt

from manim_eng import config_eng
from manim_eng._base.anchor import AnnotationAnchor, CentreAnchor, LabelAnchor
from manim_eng._base.mark import Mark
from manim_eng._base.markable import Markable
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
        **kwargs: Any,
    ) -> None:
        super().__init__(
            stroke_width=config_eng.symbol.component_stroke_width, **kwargs
        )

        self.terminals = terminals

        self._centre_anchor = CentreAnchor()
        self._label_anchor = LabelAnchor()
        self._annotation_anchor = AnnotationAnchor()

        self._body = mn.VGroup()
        self.add(self._body)

        self._construct()

        for terminal in self.terminals:
            terminal.match_style(self)
        self._body.add(*self.terminals)

        self.__set_up_anchors()
        self._label = Mark(self._label_anchor, self._centre_anchor)
        self._annotation = Mark(self._annotation_anchor, self._centre_anchor)
        self.__initialise_marks(label, annotation)

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
        """
        self._set_mark(self._label, label)
        return self

    def clear_label(self) -> Self:
        """Clear the label of the component."""
        self._clear_mark(self._label)
        return self

    def set_annotation(self, annotation: str) -> Self:
        """Set the annotation of the component.

        Parameters
        ----------
        annotation : str
            The annotation to set. Takes a TeX math mode string.
        """
        self._set_mark(self._annotation, annotation)
        return self

    def clear_annotation(self) -> Self:
        """Clear the annotation of the component."""
        self._clear_mark(self._annotation)
        return self

    def set_current(
        self, label: str, terminal: Terminal | str | None = None, **kwargs: Any
    ) -> Self:
        """Set the current label on one of the terminals of the component.

        Parameters
        ----------
        label : str | None
            The current label to set. Takes a TeX math mode string.
        terminal : Terminal | str | None
            Either a ``Terminal`` belonging to this component, or a string representing
            an attribute of this component that returns a component (e.g. ``"right"``).
            If unspecified, defaults to the first terminal in the internal terminal
            list. In the case of monopoles, this is the only terminal, and in the case
            of bipoles, this is the left terminal.

        Other Parameters
        ----------------
        **kwargs : Any
            Kwargs to pass on to the terminal's ``.set_current()`` method.

        Raises
        ------
        ValueError
            If a ``Terminal`` passed to ``terminal`` does not belong to this component.
        AttributeError
            If a string passed to ``terminal`` does not represent an existing attribute.
        ValueError
            If a string passed to ``terminal`` does not represent an attribute of this
            component that produces a ``Terminal`` instance.

        See Also
        --------
        components.base.terminal.Terminal.set_current()
        """
        terminal = self._get_or_check_terminal(terminal)
        terminal.set_current(label, **kwargs)
        return self

    def reset_current(
        self, label: str, terminal: Terminal | str | None = None, **kwargs: Any
    ) -> Self:
        """Reset the current label on one of the terminals of the component.

        **Warning:** Using this will reset all unspecified arguments to their default
        values. See the documentation of ``Terminal.reset_current()`` for more
        information.

        Parameters
        ----------
        label : str | None
            The current label to set. Takes a TeX math mode string.
        terminal : Terminal | str | None
            Either a ``Terminal`` belonging to this component, or a string representing
            an attribute of this component that returns a component (e.g. ``"right"``).
            If unspecified, defaults to the first terminal in the internal terminal
            list. In the case of monopoles, this is the only terminal, and in the case
            of bipoles, this is the left terminal.

        Other Parameters
        ----------------
        **kwargs : Any
            Kwargs to pass on to the terminal's ``.set_current()`` method.

        Raises
        ------
        ValueError
            If a ``Terminal`` passed to ``terminal`` does not belong to this component.
        AttributeError
            If a string passed to ``terminal`` does not represent an existing attribute.
        ValueError
            If a string passed to ``terminal`` does not represent an attribute of this
            component that produces a ``Terminal`` instance.

        See Also
        --------
        components.base.terminal.Terminal.reset_current()
        """
        terminal = self._get_or_check_terminal(terminal)
        terminal.reset_current(label, **kwargs)
        return self

    def clear_current(self, terminal: Terminal | str | None = None) -> Self:
        """Clear the current label on one of the terminals of the component.

        Parameters
        ----------
        terminal : Terminal | str | None
            Either a ``Terminal`` belonging to this component, or a string representing
            an attribute of this component that returns a component (e.g. ``"right"``).
            If unspecified, defaults to the first terminal in the internal terminal
            list. In the case of monopoles, this is the only terminal, and in the case
            of bipoles, this is the left terminal.

        Raises
        ------
        ValueError
            If a ``Terminal`` passed to ``terminal`` does not belong to this component.
        AttributeError
            If a string passed to ``terminal`` does not represent an existing attribute.
        ValueError
            If a string passed to ``terminal`` does not represent an attribute of this
            component that produces a ``Terminal`` instance.

        See Also
        --------
        components.base.terminal.Terminal.clear_current()
        """
        terminal = self._get_or_check_terminal(terminal)
        terminal.clear_current()
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

    def _get_or_check_terminal(self, terminal: Terminal | str | None) -> Terminal:
        """Get a terminal or check a passed terminal belongs to this component.

        Parameters
        ----------
        terminal : Terminal | str | None
            The string to use as a terminal identifier, a ``Terminal`` instance to
            verify belongs to this component, or ``None``, in which case the first
            terminal will be used.

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
        if terminal is None:
            return self.terminals[0]

        if isinstance(terminal, Terminal):
            if terminal not in self.terminals:
                raise ValueError("Passed terminal does not belong to this component.")
            return terminal

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
    def __animate_set_label(
        self, label: str, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return self.animate(**anim_args)._set_mark(self._label, label).build()

    @mn.override_animate(clear_label)
    def __animate_clear_label(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return self.animate(**anim_args)._clear_mark(self._label).build()

    @mn.override_animate(set_annotation)
    def __animate_set_annotation(
        self, label: str, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return self.animate(**anim_args)._set_mark(self._annotation, label).build()

    @mn.override_animate(clear_annotation)
    def __animate_clear_annotation(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return self.animate(**anim_args)._clear_mark(self._annotation).build()

    @mn.override_animate(set_current)
    def __animate_set_current(
        self,
        label: str,
        terminal: Terminal | str | None = None,
        anim_args: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        terminal = self._get_or_check_terminal(terminal)
        return terminal.animate(**anim_args).set_current(label, **kwargs).build()

    @mn.override_animate(reset_current)
    def __animate_reset_current(
        self,
        label: str,
        terminal: Terminal | str | None = None,
        anim_args: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        terminal = self._get_or_check_terminal(terminal)
        return terminal.animate(**anim_args).reset_current(label, **kwargs).build()

    @mn.override_animate(clear_current)
    def __animate_clear_current(
        self,
        terminal: Terminal | str | None = None,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        terminal = self._get_or_check_terminal(terminal)
        return terminal.animate(**anim_args).clear_current().build()
