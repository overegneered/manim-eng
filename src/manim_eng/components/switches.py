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
