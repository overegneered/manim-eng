"""Component symbols of switches (both lever-arm and push-button)."""

from typing import Any, Self

import manim as mn
import numpy as np

from manim_eng import config_eng
from manim_eng.components.base.switch import BipoleSwitchBase

__all__ = ["Switch", "PushSwitch", "PushToBreakSwitch", "PushToMakeSwitch"]


class Switch(BipoleSwitchBase):
    """Circuit symbol for a basic two-terminal lever-arm switch.

    Parameters
    ----------
    closed : bool
        Whether the switch should be initially closed or not.
    """

    __open_wiper_angle: float = 30 * mn.DEGREES

    def __init__(self, closed: bool = False, **kwargs: Any) -> None:
        self.wiper: mn.Line

        super().__init__(closed, **kwargs)

    def _construct(self) -> None:
        super()._construct()

        self.wiper = (
            mn.Line(
                start=self.left_node.get_center(),
                end=self.right_node.get_center(),
                stroke_width=config_eng.symbol.component_stroke_width,
            )
            .match_style(self)
            .rotate(self.__open_wiper_angle, about_point=self.left_node.get_center())
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


class PushSwitch(BipoleSwitchBase):
    """Circuit symbol for a basic push switch.

     The switch can be push-to-make or push-to-break.

    **Note:** it is recommended to use the dedicated ``PushToMakeSwitch`` and
    ``PushToBreakSwitch`` components over this component. It is available here because
    it is, after all, a complete component.

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


class PushToMakeSwitch(PushSwitch):
    """Component symbol for a push-to-make switch.

    Parameters
    ----------
    closed : bool
        Whether the switch should be initially closed or not. Defaults to open.
    """

    def __init__(self, closed: bool = False, **kwargs: Any) -> None:
        super().__init__(push_to_make=True, closed=closed, **kwargs)


class PushToBreakSwitch(PushSwitch):
    """Component symbol for a push-to-break switch.

    Parameters
    ----------
    closed : bool
        Whether the switch should be initially closed or not. Defaults to **closed**
    (this is in contrast to the other switches, which default to open).
    """

    def __init__(self, closed: bool = True, **kwargs: Any) -> None:
        super().__init__(push_to_make=False, closed=closed, **kwargs)
