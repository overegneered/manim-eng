"""Module containing the capacitor component."""

from typing import Any

import manim as mn

from manim_eng import config_eng
from manim_eng._base.component import Bipole
from manim_eng._base.terminal import Terminal


class Capacitor(Bipole):
    """Circuit symbol for a basic capacitor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.plate_half_gap = config_eng.symbol.bipole_width / 10
        self.plate_half_height = 4 * self.plate_half_gap

        super().__init__(
            Terminal(
                position=mn.LEFT * self.plate_half_gap,
                direction=mn.LEFT,
            ),
            Terminal(
                position=mn.RIGHT * self.plate_half_gap,
                direction=mn.RIGHT,
            ),
            *args,
            **kwargs,
        )

    def _construct(self) -> None:
        super()._construct()

        for direction in [mn.LEFT, mn.RIGHT]:
            plate_base = (
                direction * self.plate_half_gap + mn.DOWN * self.plate_half_height
            )
            plate = mn.Line(
                start=plate_base,
                end=plate_base + 2 * self.plate_half_height * mn.UP,
                stroke_width=config_eng.symbol.component_stroke_width,
            )
            self._body.add(plate)
