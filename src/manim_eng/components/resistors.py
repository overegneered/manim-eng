"""Component symbols of resistor-based components."""

import manim as mn

from manim_eng._config import config_eng
from manim_eng.components.base.bipole import Bipole

__all__ = ["Resistor", "Thermistor", "VariableResistor"]

from manim_eng.components.base.modifiers import SensorModifier, VariableModifier


class Resistor(Bipole):
    """Circuit symbol for a resistor."""

    def _construct(self) -> None:
        super()._construct()
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
