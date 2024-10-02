"""Base switch class and switch utility classes."""

import abc
from typing import Any, Self

import manim as mn

from manim_eng import config_eng
from manim_eng.components.base.bipole import Bipole
from manim_eng.components.base.terminal import Terminal

__all__ = ["BipoleSwitchBase"]


class OpenNode(mn.Arc):
    def __init__(self, match_to: mn.VMobject) -> None:
        super().__init__(
            radius=config_eng.symbol.node_radius,
            angle=2 * mn.PI,
            fill_color=mn.config.background_color,
            fill_opacity=match_to.stroke_opacity,
            stroke_width=config_eng.symbol.wire_stroke_width,
            stroke_color=match_to.stroke_color,
            stroke_opacity=match_to.stroke_opacity,
            z_index=10,
        )


class BipoleSwitchBase(Bipole, metaclass=abc.ABCMeta):
    """Base class for switches with two terminals.

    Note that subclasses should construct their switch models **open**.
    """

    def __init__(self, closed: bool = False, **kwargs: Any) -> None:
        half_width = config_eng.symbol.square_bipole_side_length / 2
        self.closed = False
        self.left_node = OpenNode(self).move_to(half_width * mn.LEFT)
        self.right_node = OpenNode(self).move_to(half_width * mn.RIGHT)

        super().__init__(
            Terminal(
                position=mn.LEFT * half_width,
                direction=mn.LEFT,
            ),
            Terminal(
                position=mn.RIGHT * half_width,
                direction=mn.RIGHT,
            ),
            **kwargs,
        )

        if closed:
            self.close()

    def _construct(self) -> None:
        super()._construct()
        self._body.add(self.left_node, self.right_node)

    @abc.abstractmethod
    def open(self) -> Self:
        """Open the switch, if not already open."""

    @abc.abstractmethod
    def close(self) -> Self:
        """Close the switch, if not already closed."""

    def toggle(self) -> Self:
        """Toggle the switch position (open becomes closed, closed becomes open)."""
        if self.closed:
            return self.open()
        return self.close()

    def set_closed(self, closed: bool) -> Self:
        """Set the position of the switch."""
        if closed:
            return self.close()
        return self.open()

    @mn.override_animate(toggle)
    def __animate_toggle(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation | None:
        if anim_args is None:
            anim_args = {}
        if self.closed:
            return self.animate(**anim_args).open().build()
        return self.animate(**anim_args).close().build()

    @mn.override_animate(set_closed)
    def __animate_set_closed(
        self, closed: bool, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation | None:
        if anim_args is None:
            anim_args = {}
        if closed:
            return self.animate(**anim_args).close().build()
        return self.animate(**anim_args).open().build()
