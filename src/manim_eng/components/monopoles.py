"""Component symbols of monopoles, i.e. grounds and power rails."""

from typing import Any

import manim as mn
import numpy as np

from manim_eng import config_eng
from manim_eng.components.base.monopole import Monopole

__all__ = ["VDD", "VSS", "BottomRail", "Earth", "Ground", "TopRail"]


class Earth(Monopole):
    """Circuit symbol for an earthed ground connection."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(direction=mn.UP, **kwargs)

    def _construct(self) -> None:
        super()._construct()

        half_width = config_eng.symbol.monopole_width / 2
        height = half_width
        spacing = height / 3

        for line_number in range(3):
            current_half_width = half_width * (3 - line_number) / 3
            line_centre = line_number * spacing * mn.DOWN
            line = mn.Line(
                start=line_centre + current_half_width * mn.LEFT,
                end=line_centre + current_half_width * mn.RIGHT,
            ).match_style(self)
            self._body.add(line)


class Ground(Monopole):
    """Circuit symbol for a ground connection."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(direction=mn.UP, **kwargs)

    def _construct(self) -> None:
        super()._construct()

        half_width = config_eng.symbol.monopole_width / 2
        height = half_width

        symbol = mn.Polygon(
            half_width * mn.RIGHT,
            half_width * mn.LEFT,
            height * mn.DOWN,
        ).match_style(self)
        self._body.add(symbol)


class TopRail(Monopole):
    """Circuit symbol for a top rail."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(direction=mn.DOWN, **kwargs)

    def _construct(self) -> None:
        super()._construct()

        half_width = config_eng.symbol.monopole_width / 2
        line = (
            mn.Line(
                start=half_width * mn.LEFT,
                end=half_width * mn.RIGHT,
            )
            .match_style(self)
            .set_stroke(width=config_eng.symbol.wire_stroke_width)
        )
        blob = (
            mn.Dot(
                radius=config_eng.symbol.node_radius,
            )
            .match_style(self)
            .set_fill(opacity=1.0)
        )

        self._body.add(line, blob)


class BottomRail(TopRail):
    """Circuit symbol for a bottom rail."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.rotate(mn.PI, about_point=mn.ORIGIN)


class VDD(Monopole):
    """Circuit symbol for a VDD arrow."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(direction=mn.DOWN, **kwargs)

    def _construct(self) -> None:
        super()._construct()

        half_width = config_eng.symbol.monopole_width / (2 * np.sqrt(2))

        arrow = (
            mn.VMobject()
            .match_style(self)
            .set_points_as_corners(
                [
                    half_width * mn.DL,
                    mn.ORIGIN,
                    half_width * mn.DR,
                ]
            )
        )
        self._body.add(arrow)


class VSS(VDD):
    """Circuit symbol for a VSS arrow."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.rotate(mn.PI, about_point=mn.ORIGIN)
