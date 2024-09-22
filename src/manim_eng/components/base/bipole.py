"""Module containing the Bipole base class."""

import abc
from typing import Any

import manim as mn

from manim_eng import config_eng
from manim_eng.components.base.component import Component
from manim_eng.components.base.terminal import Terminal

__all__ = ["Bipole"]


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
        half_width = config_eng.symbol.bipole_width / 2

        left = (
            left
            if left is not None
            else Terminal(position=half_width * mn.LEFT, direction=mn.LEFT)
        )
        right = (
            right
            if right is not None
            else Terminal(position=half_width * mn.RIGHT, direction=mn.RIGHT)
        )
        super().__init__([left, right], *args, **kwargs)

    def _construct(self) -> None:
        pass

    @property
    def left(self) -> Terminal:
        """Return the left-hand terminal of the component.

        Note that 'left' here is defined as when the component is unrotated. This does
        not adapt to rotation.
        """
        return self.terminals[0]

    @property
    def right(self) -> Terminal:
        """Return the right-hand terminal of the component.

        Note that 'right' here is defined as when the component is unrotated. This does
        not adapt to rotation.
        """
        return self.terminals[1]
