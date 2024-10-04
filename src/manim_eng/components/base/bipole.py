"""Base classes for bipole components."""

import abc
from typing import Any

import manim as mn

from manim_eng import config_eng
from manim_eng.components.base.component import Component
from manim_eng.components.base.terminal import Terminal

__all__ = ["Bipole", "SquareBipole"]


class Bipole(Component, metaclass=abc.ABCMeta):
    """Base class for bipole components, such as resistors and sources.

    By default, adds two terminals: one from (-0.5, 0) to (-1, 0), and one from (0.5, 0)
    to (1, 0).

    Parameters
    ----------
    left : Terminal | None
        The terminal to use as the left connection point for the component. If left
        unspecified, the terminal will be in the default position for the left terminal
        of a rectangular bipole.
    right : Terminal | None
        The terminal to use as the right connection point for the component. If left
        unspecified, the terminal will be in the default position for the right terminal
        of a rectangular bipole.
    """

    def __init__(
        self,
        left: Terminal | None = None,
        right: Terminal | None = None,
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
        super().__init__(terminals=[left, right], **kwargs)

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


class SquareBipole(Bipole, metaclass=abc.ABCMeta):
    """Base class for bipole components with a more square footprint.

    Parameters
    ----------
    left : Terminal | None
        The terminal to use as the left connection point for the component. If left
        unspecified, the terminal will be in the default position for the left terminal
        of a square bipole.
    right : Terminal | None
        The terminal to use as the right connection point for the component. If left
        unspecified, the terminal will be in the default position for the right terminal
        of a square bipole.
    """

    def __init__(
        self,
        left: Terminal | None = None,
        right: Terminal | None = None,
        **kwargs: Any,
    ) -> None:
        half_width = config_eng.symbol.square_bipole_side_length / 2
        super().__init__(
            Terminal(
                position=mn.LEFT * half_width,
                direction=mn.LEFT,
            )
            if left is None
            else left,
            Terminal(
                position=mn.RIGHT * half_width,
                direction=mn.RIGHT,
            )
            if right is None
            else right,
            **kwargs,
        )
