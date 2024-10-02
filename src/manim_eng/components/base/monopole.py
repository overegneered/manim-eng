"""Module for the Monopole base class."""

import abc
from typing import Any

import manim as mn
import manim.typing as mnt

from manim_eng.components.base.component import Component
from manim_eng.components.base.terminal import Terminal


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

    @property
    def terminal(self) -> Terminal:
        """Get the terminal of the component."""
        return self.terminals[0]
