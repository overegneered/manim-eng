"""Resistor-based components."""

import manim as mn

from manim_eng._config import config_eng
from manim_eng.components.base.bipole import Bipole

__all__ = ["Resistor", "Thermistor", "VariableResistor"]

from manim_eng.components.base.modifiers import SensorModifier, VariableModifier


class Resistor(Bipole):
    """The circuit symbol for a resistor."""

    def _construct(self) -> None:
        super()._construct()
        box = mn.Rectangle(
            width=config_eng.symbol.bipole_width,
            height=config_eng.symbol.bipole_height,
            stroke_width=config_eng.symbol.component_stroke_width,
        ).match_style(self)
        self._body.add(box)


class Thermistor(SensorModifier, Resistor):
    """The circuit symbol for a thermistor."""

    def _construct(self) -> None:
        super()._construct()


class VariableResistor(VariableModifier, Resistor):
    """The circuit symbol for a variable resistor."""

    def _construct(self) -> None:
        super()._construct()
