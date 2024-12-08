"""Modifiers that can be applied to other components to add elements.

They are applied by inheritance, and should be the *first* class a subclass inherits
from. The other requirement is that the subclass implement ``._construct()`` and call
``super()._construct()``. A bare-minimum example is shown below.

::

    class ModifiedComponent(Modifier, ComponentToModify):
        def _construct(self) -> None:
            super()._construct()
"""

import abc

import manim as mn
import numpy as np

from manim_eng import config_eng
from manim_eng.components.base.component import Component

__all__ = ["DiamondOuter", "RoundOuter", "SensorModifier", "VariableModifier"]


class RoundOuter(Component, metaclass=abc.ABCMeta):
    """Modifier to add a circular outline to a component.

    The diameter of the outline is equal to the side length of a square bipole.
    """

    def _construct(self) -> None:
        super()._construct()
        self._body.add(
            # Use an Arc instead of a Circle because it doesn't have a strange default
            # colour
            mn.Arc(
                radius=config_eng.symbol.square_bipole_side_length / 2,
                angle=mn.TAU,
            ).match_style(self)
        )


class DiamondOuter(Component, metaclass=abc.ABCMeta):
    """Modifier to add a diamond outline to a component.

    The distance between opposite points of the outline is equal to the side length of a
    square bipole.
    """

    def _construct(self) -> None:
        super()._construct()
        self._body.add(
            mn.Square(
                side_length=config_eng.symbol.square_bipole_side_length / np.sqrt(2),
            )
            .match_style(self)
            .rotate(45 * mn.DEGREES)
        )


class VariableModifier(Component, metaclass=abc.ABCMeta):
    """Modifier to add diagonal arrow to a component to signify variability."""

    def _construct(self) -> None:
        super()._construct()

        component_width = float(
            np.linalg.norm(self._body.get_right() - self._body.get_left())
        )
        component_height = float(
            np.linalg.norm(self._body.get_bottom() - self._body.get_top())
        )

        arrow_half_height = component_height * (
            1.0 if component_width > component_height else 0.5
        )
        arrow_half_height = max(
            arrow_half_height, 0.5 * config_eng.symbol.square_bipole_side_length
        )
        arrow_half_width = 0.8 * arrow_half_height

        arrow = mn.Arrow(
            start=np.array([-arrow_half_width, -arrow_half_height, 0])
            + self._body.get_center(),
            end=np.array([arrow_half_width, arrow_half_height, 0])
            + self._body.get_center(),
            buff=0,
            tip_length=config_eng.symbol.variability_arrow_tip_length,
            stroke_width=self.stroke_width,
            stroke_color=self.stroke_color,
            stroke_opacity=self.stroke_opacity,
            fill_color=self.stroke_color,
            fill_opacity=self.stroke_opacity,
        )
        self._body.add(arrow)


class SensorModifier(Component, metaclass=abc.ABCMeta):
    """Modifier to add a 'bent L' to a component to signify that it is a sensor.

    The 'bent L' will be positioned such that the main arm will pass through the
    component symbol's centre.
    """

    __min_ratio = 0.8
    __max_ratio = 1.8

    def _construct(self) -> None:
        super()._construct()

        component_width = float(
            np.linalg.norm(self._body.get_right() - self._body.get_left())
        )
        component_height = float(
            np.linalg.norm(self._body.get_bottom() - self._body.get_top())
        )

        margin = config_eng.symbol.square_bipole_side_length * 0.2
        half_width = component_width / 2
        half_height = component_height / 2

        if component_width > component_height:
            half_height += margin
        else:
            half_width += margin

        ratio = half_width / half_height
        if ratio < self.__min_ratio:
            half_width = self.__min_ratio * half_height
        if ratio > self.__max_ratio:
            half_height = half_width / self.__max_ratio

        base_length = 0.5 * half_width

        bottom_left = np.array([-half_width, -half_height, 0])
        bottom_middle = np.array([-(half_width - base_length), -half_height, 0])
        top_right = np.array([half_width, half_height, 0])

        main_midpoint_offset = (bottom_middle + top_right) / 2

        tick = (
            mn.VMobject()
            .match_style(self)
            .set_points_as_corners([bottom_left, bottom_middle, top_right])
            .move_to(self._body.get_center() - main_midpoint_offset)
        )

        self._body.add(tick)
