"""Base classes for tripole components."""

import abc
from typing import Any

import manim as mn

from manim_eng import config_eng
from manim_eng.components.base.component import Component
from manim_eng.components.base.terminal import Terminal

__all__ = ["Tripole"]

class Tripole(Component, metaclass=abc.ABCMeta):
    """Base class for tripole components, such as transistors and MOSFETs.

    By default, adds three terminals: one from (-0.5, 0) to (-1, 0), one from (0.5, 0)
    to (1, 0), and one from (0, 0.5) to (0, 1).

    Parameters
    ----------
    left : Terminal | None
        The terminal to use as the left connection point for the component. If left
        unspecified, the terminal will be in the default position for the left terminal
        of a rectangular tripole.
    right : Terminal | None
        The terminal to use as the right connection point for the component. If left
        unspecified, the terminal will be in the default position for the right terminal
        of a rectangular tripole.
    top : Terminal | None
        The terminal to use as the top connection point for the component. If left
        unspecified, the terminal will be in the default position for the top terminal
        of a rectangular tripole.
    """

    def __init__(
        self,
        left: Terminal | None = None,
        right: Terminal | None = None,
        top: Terminal | None = None,
        **kwargs: Any,
    ) -> None:
        half_width = config_eng.symbol.tripole_width / 2

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
        top = (
            top
            if top is not None
            else Terminal(position=config_eng.symbol.tripole_height * mn.UP, direction=mn.UP)
        )
        super().__init__(terminals=[left, right, top], **kwargs)

    def _construct(self) -> None:
        pass

    @property
    def left(self) -> Terminal:
        """Return the left-hand terminal of the component.

        Note that 'left' here is defined as when the component is unrotated. This does not
        necessarily correspond to the actual position of the terminal after rotation.
        """
        return self.terminals[0]

    @property
    def right(self) -> Terminal:
        """Return the right-hand terminal of the component.
        
        Note that 'right' here is defined as when the component is unrotated. This does not
        necessarily correspond to the actual position of the terminal after rotation.
        """
        return self.terminals[1]

    @property
    def top(self) -> Terminal:
        """Return the top-hand terminal of the component.

        Note that 'top' here is defined as when the component is unrotated. This does not
        necessarily correspond to the actual position of the terminal after rotation.
        """
        return self.terminals[2]