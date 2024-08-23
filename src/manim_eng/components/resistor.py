"""Resistor-based components."""

import manim as mn
import numpy as np

from ._component.component import Bipole

__all__ = ["Resistor", "Thermistor", "VariableResistor"]

from .._config import config_eng


class Resistor(Bipole):
    """The circuit symbol for a resistor."""

    def _construct(self) -> None:
        super()._construct()
        box = mn.Rectangle(
            width=1, height=0.4, stroke_width=config_eng.symbol.component_stroke_width
        )
        self._body.add(box)


class Thermistor(Resistor):
    """The circuit symbol for a thermistor."""

    def _construct(self) -> None:
        super()._construct()

        tick_base = mn.Line(np.array([-0.5, -0.35, 0]), np.array([-0.2, -0.35, 0]))
        tick_diagonal = mn.Line(np.array([-0.2, -0.35, 0]), np.array([0.5, 0.35, 0]))
        self._body.add(tick_base, tick_diagonal)


class VariableResistor(Resistor):
    """The circuit symbol for a variable resistor."""

    def _construct(self) -> None:
        super()._construct()

        arrow = mn.Arrow(
            np.array([-0.35, -0.4, 0]),
            np.array([0.35, 0.4, 0]),
            buff=0,
            max_tip_length_to_length_ratio=0.125,
            stroke_width=config_eng.symbol.component_stroke_width,
        )
        self._body.add(arrow)
