"""Base class for switches and implementation helper class."""

import abc
from typing import Any, Self

import manim as mn
import numpy as np

from manim_eng import config_eng
from manim_eng.components import node
from manim_eng.components.base.bipole import Bipole
from manim_eng.components.base.terminal import Terminal

__all__ = ["BipoleSwitchBase", "PushSwitchBase"]


class BipoleSwitchBase(Bipole, metaclass=abc.ABCMeta):
    """Base class for switches with two terminals.

    Note that subclasses should construct their switch models **open**.
    """

    def __init__(self, closed: bool = False, **kwargs: Any) -> None:
        half_width = config_eng.symbol.square_bipole_side_length / 2
        self.closed: bool = closed
        self.left_node = node._create_node_blob(self, open_=True).move_to(
            half_width * mn.LEFT
        )
        self.right_node = node._create_node_blob(self, open_=True).move_to(
            half_width * mn.RIGHT
        )

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


class PushSwitchBase(BipoleSwitchBase):
    """Circuit symbol for a basic push switch.

     The switch can be push-to-make or push-to-break.

    Parameters
    ----------
    push_to_make : bool
        Whether the switch should be push-to-make or push-to-break. ``True`` produces a
        push-to-make, ``False`` produces a push-to-break.
    closed : bool
        Whether the switch should be initially closed or not.
    """

    __travel = 1.5 * config_eng.symbol.node_radius

    def __init__(self, push_to_make: float, closed: bool, **kwargs: Any) -> None:
        self.push_to_make = push_to_make
        self.__button = mn.VGroup()
        super().__init__(closed, **kwargs)

        # Make sure the label anchor is above the greatest extension of the button
        # (i.e. when it's closed)
        if not push_to_make:
            self._label_anchor.shift(self.__travel * mn.UP)

    def _construct(self) -> None:
        super()._construct()

        if self.push_to_make:
            start = self.left_node.get_top() + self.__travel * mn.UP
            end = self.right_node.get_top() + self.__travel * mn.UP
        else:
            start = self.left_node.get_bottom() + self.__travel * mn.DOWN
            end = self.right_node.get_bottom() + self.__travel * mn.DOWN

        button_centre = self.get_top() + self.__travel * mn.UP
        button_half_width = config_eng.symbol.square_bipole_side_length / 8

        contact = mn.Line(
            start=start,
            end=end,
            stroke_width=config_eng.symbol.component_stroke_width,
        ).match_style(self)
        connector = mn.Line(
            start=contact.get_center(),
            end=button_centre,
            stroke_width=config_eng.symbol.component_stroke_width,
        ).match_style(self)
        button = mn.Line(
            start=button_centre + button_half_width * mn.LEFT,
            end=button_centre + button_half_width * mn.RIGHT,
            stroke_width=config_eng.symbol.component_stroke_width,
        ).match_style(self)
        self.__button.add(contact, connector, button)
        self._body.add(self.__button)

    def open(self) -> Self:
        """Open the switch, if not already open."""
        if not self.closed:
            return self
        direction = np.cross(
            mn.normalize(self.left_node.get_center() - self.right_node.get_center()),
            mn.OUT if self.push_to_make else mn.IN,
        )
        self.__button.shift(direction * self.__travel)
        self.closed = False
        return self

    def close(self) -> Self:
        """Close the switch, if not already closed."""
        if self.closed:
            return self
        direction = np.cross(
            mn.normalize(self.left_node.get_center() - self.right_node.get_center()),
            mn.IN if self.push_to_make else mn.OUT,
        )
        self.__button.shift(direction * self.__travel)
        self.closed = True
        return self
