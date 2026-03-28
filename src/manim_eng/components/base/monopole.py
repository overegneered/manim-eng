"""Contains the Monopole base class."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, Self

import manim as mn
import manim.typing as mnt

from manim_eng._base import Mark
from manim_eng.components.base.component import Component
from manim_eng.components.base.pin import Pin

if TYPE_CHECKING:
    from manim_eng.circuits.node import Node

__all__ = ["Monopole"]


class Monopole(Component, metaclass=abc.ABCMeta):
    """Base class for monopole components, such as grounds and rails.

    Creates a single pin in the direction of ``direction`` with its start at the
    origin.

    Parameters
    ----------
    direction : Vector3D
        The direction the pin of the component should face.
    """

    def __init__(self, direction: mnt.Vector3D, **kwargs: Any) -> None:
        pin = Pin(
            position=mn.ORIGIN,
            direction=direction,
            parent=self,
        )
        super().__init__(pins=[pin], **kwargs)

        self._label_anchor.move_to(self.get_critical_point(-direction))
        self.update()
        self.remove(self._annotation_anchor)

    @property
    def pin(self) -> Pin:
        """Get the pin of the component."""
        return self.pins[0]

    def align_monopole(
        self,
        other: Pin | mnt.Point3D | Node | Monopole,
        direction: mnt.Vector3D | None = None,
    ) -> Self:
        """Aligns the monopole's pin with another point or component.

        Moves this component along the line perpendicular to ``direction`` such that the
        line between the end of this component's pin and ``other``
        has direction vector ``direction``.

        Parameters
        ----------
        other : Pin | Point3D | Node | Monopole
            A ``Pin`` belonging to another component, a ``Node``, a ``Monopole``
            (for which its single pin is selected), or a point in space.
        direction : Vector3D | None
            The direction to align the pins in. If not supplied, uses
            ``self.pin``'s direction.

        Raises
        ------
        ValueError
            If ``other`` belongs to this component (if it is a ``Pin``)
            or if ``other`` *is* this component (if it is a ``Node`` or
            ``Monopole``).

        Notes
        -----
        In geometric terms, the component in moved such that the end of
        this monopole's pin is at the intersection of the lines that

        - Have direction vector perpendicular to ``direction`` and go through the
            current position of the end of this monopole's pin; and
        - Have direction vector ``direction`` and go through the end of
            ``other`` (in the case that it is a ``Pin``) or through ``other`` (in
            the case that it is a point).
        """
        return super().align_pin(self.pin, other, direction)

    @property
    def annotation(self) -> Mark:
        """Monopoles do not have annotations.

        **THIS WILL FAIL.**
        """
        raise NotImplementedError(
            "`Monopole`s have no annotations. Please use `label` instead."
        )
