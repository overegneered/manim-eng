"""Modifiers that can be applied to other components to add elements."""

import abc

import manim as mn
import numpy as np

from manim_eng import config_eng
from manim_eng.components.base.component import Component


class RoundOuter(Component, metaclass=abc.ABCMeta):
    """Circular component outline."""

    def _construct(self) -> None:
        super()._construct()
        self._body.add(
            # Use an Arc instead of a Circle because it doesn't have a strange default
            # colour
            mn.Arc(
                radius=config_eng.symbol.square_bipole_side_length / 2,
                angle=mn.TAU,
                stroke_width=config_eng.symbol.component_stroke_width,
            )
        )


class DiamondOuter(Component, metaclass=abc.ABCMeta):
    """Diamond component outline."""

    def _construct(self) -> None:
        super()._construct()
        self._body.add(
            mn.Square(
                side_length=config_eng.symbol.square_bipole_side_length / np.sqrt(2),
                stroke_width=config_eng.symbol.component_stroke_width,
            ).rotate(45 * mn.DEGREES)
        )
