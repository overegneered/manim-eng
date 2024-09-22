"""Resistor-based components."""

import manim as mn

from manim_eng._config import config_eng
from manim_eng.components.base.bipole import Bipole

__all__ = ["Resistor", "Thermistor", "VariableResistor"]


class Resistor(Bipole):
    """The circuit symbol for a resistor."""

    def _construct(self) -> None:
        super()._construct()
        box = mn.Rectangle(
            width=config_eng.symbol.bipole_width,
            height=config_eng.symbol.bipole_height,
            stroke_width=config_eng.symbol.component_stroke_width,
        )
        self._body.add(box)


class Thermistor(Resistor):
    """The circuit symbol for a thermistor."""

    def _construct(self) -> None:
        super()._construct()

        half_width = 0.5 * config_eng.symbol.bipole_width
        half_height = 0.8 * config_eng.symbol.bipole_height
        base_length = 0.3 * config_eng.symbol.bipole_width

        tick_points = [
            (-half_width, -half_height, 0),
            (-(half_width - base_length), -half_height, 0),
            (half_width, half_height, 0),
        ]
        tick = mn.VMobject().set_points_as_corners(tick_points)

        self._body.add(tick)


class VariableResistor(Resistor):
    """The circuit symbol for a variable resistor."""

    def _construct(self) -> None:
        super()._construct()

        half_width = 0.35 * config_eng.symbol.bipole_width
        half_height = config_eng.symbol.bipole_height

        arrow = mn.Arrow(
            start=(-half_width, -half_height, 0),
            end=(half_width, half_height, 0),
            buff=0,
            max_tip_length_to_length_ratio=0.125,
            stroke_width=config_eng.symbol.component_stroke_width,
        )
        self._body.add(arrow)
