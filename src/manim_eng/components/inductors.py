"""Component symbols of inductor-based components."""

import manim as mn

from manim_eng import config_eng
from manim_eng.components.base.bipole import Bipole

__all__ = ["InductiveSensor", "Inductor", "VariableInductor"]

from manim_eng.components.base.modifiers import SensorModifier, VariableModifier


class Inductor(Bipole):
    """Circuit symbol for an inductor."""

    def _construct(self) -> None:
        super()._construct()

        arc_radius = config_eng.symbol.bipole_width / 8
        for i in range(4):
            centre_x = arc_radius * (-3 + i * 2)
            arc = mn.Arc(
                radius=arc_radius,
                start_angle=mn.PI,
                angle=-mn.PI,
                arc_center=centre_x * mn.RIGHT,
                stroke_width=config_eng.symbol.component_stroke_width,
            ).match_style(self)
            self._body.add(arc)

        # Avoid the 'cut off' look at the ends of the inductor, due to the interface
        # between the terminal and inductor body
        for correction_direction in [mn.LEFT, mn.RIGHT]:
            visual_correction = (
                mn.VMobject()
                .match_style(self)
                .set_points_as_corners(
                    [
                        0.001 * mn.UP,
                        mn.ORIGIN,
                        0.001 * correction_direction,
                    ]
                )
                .shift(correction_direction * 0.5 * config_eng.symbol.bipole_width)
            )
            self._body.add(visual_correction)


class InductiveSensor(SensorModifier, Inductor):
    """Circuit symbol for an inductive sensor."""

    def _construct(self) -> None:
        super()._construct()


class VariableInductor(VariableModifier, Inductor):
    """Circuit symbol for a variable inductor."""

    def _construct(self) -> None:
        super()._construct()
