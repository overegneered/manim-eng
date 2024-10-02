"""Switches (both lever-arm and push-button)."""

from typing import Any, Self

import manim as mn

from manim_eng import config_eng
from manim_eng.components.base.switch import BipoleSwitchBase


class Switch(BipoleSwitchBase):
    """Basic two-terminal lever-arm switch.

    Parameters
    ----------
    closed : bool
        Whether the switch should be initially closed or not.
    """

    __open_wiper_angle: float = 30 * mn.DEGREES

    def __init__(self, closed: bool = False, **kwargs: Any) -> None:
        self.wiper: mn.Line

        super().__init__(closed, **kwargs)

        self.wiper.rotate(
            self.__open_wiper_angle, about_point=self.left_node.get_center()
        )
        self._label_anchor.move_to(self._body.get_top())
        self.update()
        if self.closed:
            self.wiper.rotate(
                -self.__open_wiper_angle, about_point=self.left_node.get_center()
            )

    def _construct(self) -> None:
        super()._construct()

        self.wiper = mn.Line(
            start=self.left_node.get_center(),
            end=self.right_node.get_center(),
            stroke_width=config_eng.symbol.wire_stroke_width,
        )

        self._body.add(self.wiper)

    def open(self) -> Self:
        """Open the switch, if not already open."""
        if not self.closed:
            return self
        self.wiper.rotate(
            self.__open_wiper_angle, about_point=self.left_node.get_center()
        )
        self.closed = False
        return self

    def close(self) -> Self:
        """Close the switch, if not already closed."""
        if self.closed:
            return self
        self.wiper.rotate(
            -self.__open_wiper_angle, about_point=self.left_node.get_center()
        )
        self.closed = True
        return self

    @mn.override_animate(open)
    def __animate_open(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation | None:
        if anim_args is None:
            anim_args = {}
        if not self.closed:
            return None
        self.closed = False
        return mn.Rotate(
            self.wiper,
            angle=self.__open_wiper_angle,
            about_point=self.left_node.get_center(),
            **anim_args,
        )

    @mn.override_animate(close)
    def __animate_close(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation | None:
        if anim_args is None:
            anim_args = {}
        if self.closed:
            return None
        self.closed = True
        return mn.Rotate(
            self.wiper,
            angle=-self.__open_wiper_angle,
            about_point=self.left_node.get_center(),
            **anim_args,
        )
