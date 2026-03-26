"""Component symbols of capacitor-based components."""

from typing import Any

import manim as mn

from manim_eng import config_eng
from manim_eng.components.base.bipole import Bipole
from manim_eng.components.base.modifiers import SensorModifier, VariableModifier
from manim_eng.components.base.terminal import Terminal

__all__ = ["CapacitiveSensor", "Capacitor", "PolarizedCapacitor", "VariableCapacitor"]


class Capacitor(Bipole):
    """Circuit symbol for a basic capacitor."""

    def __init__(
        self, draw_left_plate: bool = True, draw_right_plate: bool = True, **kwargs: Any
    ) -> None:
        self._plate_half_gap = config_eng.symbol.plate_gap / 2
        self._plate_half_height = config_eng.symbol.plate_height / 2
        self.__plates = []
        if draw_left_plate:
            self.__plates.append(mn.LEFT)
        if draw_right_plate:
            self.__plates.append(mn.RIGHT)

        super().__init__(
            Terminal(
                position=mn.LEFT * self._plate_half_gap,
                direction=mn.LEFT,
            ),
            Terminal(
                position=mn.RIGHT * self._plate_half_gap,
                direction=mn.RIGHT,
            ),
            **kwargs,
        )

    def _construct(self) -> None:
        super()._construct()

        for direction in self.__plates:
            plate_base = (
                direction * self._plate_half_gap + mn.DOWN * self._plate_half_height
            )
            plate = mn.Line(
                start=plate_base,
                end=plate_base + 2 * self._plate_half_height * mn.UP,
                stroke_width=config_eng.symbol.component_stroke_width,
            ).match_style(self)
            self._body.add(plate)


class PolarizedCapacitor(Capacitor):
    """Circuit symbol for a polarized capacitor.

    The ``left`` pin is the positive pin, and the ``right`` pin is the negative pin.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            draw_right_plate=False, **kwargs
        )  # only draw the left plate as a vertical line

    def _construct(self) -> None:
        super()._construct()
        center = mn.RIGHT * (2 * self._plate_half_height + self._plate_half_gap)
        arc = mn.Arc(
            2 * self._plate_half_height, mn.PI * 5 / 6, mn.PI / 3, arc_center=center
        ).match_style(self)
        marker = mn.Text(
            "+", font_size=config_eng.symbol.terminal_name_font_size
        ).match_style(self)
        marker.next_to(self._body[0], mn.LEFT, buff=2 * self._plate_half_gap).shift(
            0.5 * self._plate_half_height * mn.UP
        )
        self._body.add(arc, marker)


class CapacitiveSensor(SensorModifier, Capacitor):
    """Circuit symbol for a capacitive sensor."""

    def _construct(self) -> None:
        super()._construct()


class VariableCapacitor(VariableModifier, Capacitor):
    """Circuit symbol for a variable capacitor."""

    def _construct(self) -> None:
        super()._construct()
