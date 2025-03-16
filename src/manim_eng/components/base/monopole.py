"""Contains the Monopole base class."""

from __future__ import annotations

import abc
from typing import Any, Self

import manim as mn
import manim.typing as mnt

from manim_eng.components.base.component import Component
from manim_eng.components.base.terminal import Terminal
from manim_eng.components.node import Node
from manim_eng.units import Value

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

    def align_monopole(
        self,
        other: Terminal | mnt.Point3D | Node | Monopole,
        direction: mnt.Vector3D | None = None,
    ) -> Self:
        """Aligns the monopole's terminal with another point or component.

        Moves this component along the line perpendicular to ``direction`` such that the
        line between the end of this component's terminal and ``other``
        has direction vector ``direction``.

        Parameters
        ----------
        other : Terminal | Point3D | Node | Monopole
            A ``Terminal`` belonging to another component, a ``Node``, a ``Monopole``
            (for which its single terminal is selected), or a point in space.
        direction : Vector3D | None
            The direction to align the terminals in. If not supplied, uses
            ``self_terminal``'s direction.

        Raises
        ------
        ValueError
            If ``other`` belongs to this component (if it is a ``Terminal``)
            or if ``other`` *is* this component (if it is a ``Node`` or
            ``Monopole``).

        Notes
        -----
        In geometric terms, the component in moved such that the end of
        this monopole's terminal is at the intersection of the lines that

        - Have direction vector perpendicular to ``direction`` and go through the
            current position of the end of this monopole's terminal; and
        - Have direction vector ``direction`` and go through the end of
            ``other`` (in the case that it is a ``Terminal``) or through ``other`` (in
            the case that it is a point).
        """
        return super().align_terminal(self.terminal, other, direction)

    def set_annotation(self, annotation: str | Value) -> Self:
        """Fails for monopoles, as they do not have annotations."""
        raise NotImplementedError(
            "Monopoles have no annotation. Please use `.set_label()`."
        )

    def clear_annotation(self) -> Self:
        """Fails for monopoles, as they do not have annotations."""
        raise NotImplementedError(
            "Monopoles have no annotation. Please use `.clear_label()`."
        )
