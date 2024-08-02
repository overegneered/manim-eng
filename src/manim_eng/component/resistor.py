"""Resistor-based components."""

import manim as mn
import numpy as np

from .._base.wire import COMPONENT_STROKE_WIDTH, Wire
from ._component import Bipole

__all__ = ["Resistor", "Thermistor", "VariableResistor"]


class Resistor(Bipole):
    """The circuit symbol for a resistor."""

    def _construct(self) -> None:
        super()._construct()
        terminal_l = Wire(self.left.position, self.left.position / 2)
        box = mn.Rectangle(width=1, height=0.4)
        terminal_r = Wire(self.right.position / 2, self.right.position)
        self._body.add(terminal_l, box, terminal_r)


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
            stroke_width=COMPONENT_STROKE_WIDTH,
        )
        self._body.add(arrow)
