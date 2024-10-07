"""Contains the Monopole base class."""

import abc
from typing import Any, Self

import manim as mn
import manim.typing as mnt

from manim_eng.components.base.component import Component
from manim_eng.components.base.terminal import Terminal

__all__ = ["Monopole"]


class Monopole(Component, metaclass=abc.ABCMeta):
    """Base class for monopole components, such as grounds and rails.

    Creates a single terminal in the direction of ``direction`` with its start at the
    origin.

    Parameters
    ----------
    direction : Vector3D
        The direction the terminal of the component should face.
    """

    def __init__(self, direction: mnt.Vector3D, **kwargs: Any) -> None:
        terminal = Terminal(
            position=mn.ORIGIN,
            direction=direction,
        )
        super().__init__(terminals=[terminal], **kwargs)

        self._label_anchor.move_to(self.get_critical_point(-direction))
        self.update()
        self.remove(self._annotation_anchor)

    @property
    def terminal(self) -> Terminal:
        """Get the terminal of the component."""
        return self.terminals[0]

    def set_annotation(self, annotation: str) -> Self:
        """Fails for monopoles, as they do not have annotations."""
        raise NotImplementedError(
            "Monopoles have no annotation. Please use `.set_label()`."
        )

    def clear_annotation(self) -> Self:
        """Fails for monopoles, as they do not have annotations."""
        raise NotImplementedError(
            "Monopoles have no annotation. Please use `.clear_label()`."
        )

    def set_current(self, label: str, out: bool = False, below: bool = False) -> Self:
        """Set the current label on the monopole's single terminal.

        Parameters
        ----------
        label : str
            The current label to set. Takes a TeX math mode string.
        out : bool
            Whether the arrow accompanying the annotation should point out (away from
            the body of the component to which the terminal is attached), or in (towards
            the component, this is the default).
        below : bool
            Whether the annotation should be placed below the current arrow, or above it
            (which is the default). Note that 'below' here is defined as below the
            terminal when it is pointing right.
        """
        self.terminal.reset_current(label, out=out, below=below)
        return self

    def clear_current(self) -> Self:
        """Clear the current label on the monopole's single terminal."""
        self.terminal.clear_current()
        return self

    @mn.override_animate(set_current)
    def __animate_set_current(
        self,
        label: str,
        out: bool = False,
        below: bool = False,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return (
            self.terminal.animate(**anim_args)
            .set_current(label, out=out, below=below)
            .build()
        )

    @mn.override_animate(clear_current)
    def __animate_clear_current(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}
        return self.terminal.animate(**anim_args).clear_current().build()
