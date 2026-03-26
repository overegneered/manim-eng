"""Component symbols of resistor-based components."""

from typing import Any, Self, cast

import manim as mn
import numpy as np

from manim_eng._config import config_eng
from manim_eng.components.base.bipole import Bipole
from manim_eng.components.base.terminal import Terminal

__all__ = ["Resistor", "Thermistor", "VariableResistor", "VariableResistor3Pin"]

from manim_eng.components.base.modifiers import SensorModifier, VariableModifier


class Resistor(Bipole):
    """Circuit symbol for a resistor."""

    def _construct(self) -> None:
        super()._construct()
        if config_eng.symbol.resistor_standard == "ANSI":
            width = config_eng.symbol.bipole_width
            height = config_eng.symbol.bipole_height
            start = np.array([-width / 2, 0, 0])
            stepw = width / 12
            points = [
                start,
                start + np.array([stepw, height / 2, 0]),
                start + np.array([3 * stepw, -height / 2, 0]),
                start + np.array([5 * stepw, height / 2, 0]),
                start + np.array([7 * stepw, -height / 2, 0]),
                start + np.array([9 * stepw, height / 2, 0]),
                start + np.array([11 * stepw, -height / 2, 0]),
                start + np.array([width, 0, 0]),
            ]
            zigzag = mn.VMobject()
            zigzag.start_new_path(points[0])
            for p in points[1:]:
                zigzag.add_line_to(p)
            zigzag.match_style(self)
            self._body.add(zigzag)
        elif config_eng.symbol.resistor_standard == "IEC":
            box = mn.Rectangle(
                width=config_eng.symbol.bipole_width,
                height=config_eng.symbol.bipole_height,
            ).match_style(self)
            self._body.add(box)


class Thermistor(SensorModifier, Resistor):
    """Circuit symbol for a thermistor."""

    def _construct(self) -> None:
        super()._construct()


class VariableResistor(VariableModifier, Resistor):
    """Circuit symbol for a variable resistor."""

    def _construct(self) -> None:
        super()._construct()


class VariableResistor3Pin(Resistor):
    """Circuit symbol for a 3-pin variable resistor.

    Parameters
    ----------
    wiper_pos : float, optional
        The initial position of the wiper, represented by a value between 0 and 1.
        Defaults to 0.5.
    """

    def __init__(self, wiper_pos: float = 0.5) -> None:
        self.__wiper_pos = wiper_pos
        self.__arrow: mn.Arrow | None = None
        super().__init__()
        width = config_eng.symbol.bipole_width
        half_height = config_eng.symbol.bipole_height * 0.5
        arrow_height = config_eng.symbol.bipole_height
        wiper_terminal = Terminal(
            position=np.array(
                [-width / 2 + width * wiper_pos, half_height + arrow_height, 0.0]
            ),
            direction=mn.UP,
        )
        self._terminals.add(wiper_terminal)

    def _construct(self) -> None:
        super()._construct()
        width = config_eng.symbol.bipole_width
        half_height = config_eng.symbol.bipole_height * 0.5
        arrow_height = config_eng.symbol.bipole_height
        start = np.array(
            [-width / 2 + width * self.__wiper_pos, half_height + arrow_height, 0.0]
        )
        end = start.copy()
        end[1] = half_height
        self.__arrow = mn.Arrow(
            start,
            end,
            buff=0,
            tip_length=config_eng.symbol.arrow_tip_length,
            max_tip_length_to_length_ratio=0.5,
            max_stroke_width_to_length_ratio=10.0,
            stroke_width=self.stroke_width,
            color=self.stroke_color,
            stroke_opacity=self.stroke_opacity,
            fill_opacity=self.stroke_opacity,
        )
        self._body.add(self.__arrow)

    @property
    def top(self) -> Terminal:
        """Return the top terminal of the variable resistor (i.e. the wiper)."""
        return cast(Terminal, self._terminals.submobjects[-1])

    @property
    def wiper(self) -> Terminal:
        """Return the top terminal of the variable resistor (i.e. the wiper)."""
        return self.top

    @property
    def wiper_pos(self) -> float:
        """Return the position of the wiper, between 0 and 1.

        0 represents the wiper being in the leftmost position. 1 represents the wiper
        being in the rightmost position.
        """
        return self.__wiper_pos

    def set_wiper_pos(self, pos: float) -> Self:
        """Set the wiper position of the variable resistor."""
        if pos < 0 or pos > 1:
            raise ValueError(f"Invalid wiper position: {pos}")
        self.__wiper_pos = pos
        self.update()
        return self

    def __wiper_pos_updater(self) -> None:
        """When the wiper position changes, update the position of submobjects."""
        # Try not to add this as an updater for the object.
        width = config_eng.symbol.bipole_width
        half_height = config_eng.symbol.bipole_height * 0.5
        arrow_height = config_eng.symbol.bipole_height
        center = 0.5 * (self.left.end + self.right.end)
        up = self.wiper.direction
        left = self.left.direction
        wiper_pos = self.__wiper_pos

        # Move the arrow
        if self.__arrow is not None:
            self.__arrow.move_to(
                center
                + (half_height + 0.5 * arrow_height) * up
                + (wiper_pos - 0.5) * width * left
            )
        # Move the terminal
        terminal_length = self.wiper._line.get_length()
        self.wiper.move_to(
            center
            + (half_height + arrow_height + 0.5 * terminal_length) * up
            + (wiper_pos - 0.5) * width * left
        )

    @mn.override_animate(set_wiper_pos)
    def __animate_set_wiper_pos(
        self, pos: float, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation | None:
        value_tracker = mn.ValueTracker(self.__wiper_pos)

        def update_func(mob: Self) -> None:
            mob.__wiper_pos = value_tracker.get_value()
            mob.__wiper_pos_updater()

        return mn.AnimationGroup(
            value_tracker.animate.set_value(pos),
            mn.UpdateFromFunc(self, update_func),
            **anim_args,
        )
