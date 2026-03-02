"""Component symbols of resistor-based components."""

import numpy as np
import manim as mn

from manim_eng._config import config_eng
from manim_eng.components.base.bipole import Bipole

__all__ = ["Resistor", "Thermistor", "VariableResistor"]

from manim_eng.components.base.modifiers import SensorModifier, VariableModifier


class Resistor(Bipole):
    """Circuit symbol for a resistor."""

    def _construct(self) -> None:
        super()._construct()
        if config_eng.symbol.resistor_standard == 'ANSI':
            width = config_eng.symbol.bipole_width
            height = config_eng.symbol.bipole_height
            start = np.array([-width/2, 0, 0])
            stepw = width / 12
            points = [
                start,
                start + [stepw, height/2, 0],
                start + [3*stepw, -height/2, 0],
                start + [5*stepw, height/2, 0],
                start + [7*stepw, -height/2, 0],
                start + [9*stepw, height/2, 0],
                start + [11*stepw, -height/2, 0],
                start + [width, 0, 0],
            ]
            zigzag = mn.VMobject()
            zigzag.start_new_path(points[0])
            for p in points[1:]:
                zigzag.add_line_to(p)
            zigzag.match_style(self)
            self._body.add(zigzag)
        elif config_eng.symbol.resistor_standard == 'IEC':
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
