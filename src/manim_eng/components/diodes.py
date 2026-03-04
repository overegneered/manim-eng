"""Component symbols of diodes."""

from typing import Any, Self

import manim as mn
import numpy as np

from manim_eng import config_eng
from manim_eng.components.base.bipole import SquareBipole
from manim_eng.components.base.terminal import Terminal

__all__ = ["LED", "Diode", "Photodiode", "SchottkyDiode", "TunnelDiode", "ZenerDiode"]


class Diode(SquareBipole):
    """Circuit symbol for a diode."""

    def __init__(self, **kwargs: Any) -> None:
        self._diode_triangle: mn.Triangle | None = None
        super().__init__(**kwargs)

    def _construct(
        self,
        opacity: float = 0.0,
        fill_color: mn.ManimColor | None = None,
        draw_line: bool = True,
    ) -> None:
        """Construct a basic diode.

        Parameters
        ----------
        opacity: float
            Opacity of the fill color in the diode's triangle. Defaults to ``0.0``.
        draw_line : bool
            Whether or not to draw the diode line. Defaults to ``True``. Set to
            ``False`` if you wish to draw the line yourself (i.e. if you're extending it
            and drawing the whole thing yourself prevents joining artefacts).
        """
        super()._construct()

        width = config_eng.symbol.square_bipole_side_length
        radius = (2 / 3) * width
        half_height = np.sqrt(3) * radius / 2
        line_start = 0.5 * width * mn.RIGHT

        triangle = (
            mn.Triangle(
                start_angle=0,
                radius=radius,
            )
            .match_style(self)
            .set_fill(color=fill_color, opacity=opacity)
            .shift((1 / 12) * mn.LEFT)
        )
        self._diode_triangle = triangle
        self._body.add(triangle)

        if draw_line:
            line = mn.Line(
                start=line_start + half_height * mn.DOWN,
                end=line_start + half_height * mn.UP,
            ).match_style(self)
            self._body.add(line)

    @property
    def positive(self) -> Terminal:
        """Return the positive terminal of the diode."""
        return self.left

    @property
    def negative(self) -> Terminal:
        """Return the negative terminal of the diode."""
        return self.right

    @property
    def anode(self) -> Terminal:
        """Return the anode (positive terminal) of the diode."""
        return self.positive

    @property
    def cathode(self) -> Terminal:
        """Return the cathode (negative terminal) of the diode."""
        return self.negative


class LED(Diode):
    """Circuit symbol for an LED.

    Parameters
    ----------
    led_color : manim.ManimColor
        The color of the lamp.
    opacity : float
        The initial opacity of the lamp. Default to 0.0.
    """

    def __init__(
        self,
        led_color: mn.ManimColor = mn.PURE_RED,
        opacity: float = 0.0,
        **kwargs: Any,
    ) -> None:
        self._led_color = led_color
        self._opacity = opacity
        super().__init__(**kwargs)

    def _construct(self) -> None:  # type: ignore[override]
        super()._construct(fill_color=self._led_color, opacity=self._opacity)

        top_left = self._body.get_corner(mn.UL)
        right = self._body.get_right()
        perp_direction = mn.normalize(right - top_left)
        perp_length = np.linalg.norm(top_left - right)
        arrow_direction = np.cross(perp_direction, mn.IN)

        arrow_length = 0.55 * perp_length

        for alpha in [0.15, 0.35]:
            arrow_start = (
                top_left + alpha * perp_direction + 0.15 * perp_length * arrow_direction
            )
            arrow_end = arrow_start + arrow_length * arrow_direction

            self._body.add(
                mn.Arrow(
                    start=arrow_start,
                    end=arrow_end,
                    buff=0,
                    tip_length=config_eng.symbol.arrow_tip_length,
                    stroke_width=config_eng.symbol.component_stroke_width,
                    color=self.stroke_color,
                    stroke_opacity=self.stroke_opacity,
                    fill_opacity=self.stroke_opacity,
                )
            )

    def light_up(self) -> Self:
        """Light up the LED.

        This method sets the LED's opacity to 1.0.
        """
        self._opacity = 1.0
        if self._diode_triangle is not None:
            self._diode_triangle.set_fill(opacity=1.0)
        return self

    def extinguish(self) -> Self:
        """Extinguish the LED, if it hasn't.

        This method sets the LED's opacity to 0.0.
        """
        self._opacity = 0.0
        if self._diode_triangle is not None:
            self._diode_triangle.set_fill(opacity=0.0)
        return self

    @mn.override_animate(light_up)
    def __animate_light_up(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation | None:
        if anim_args is None:
            anim_args = {}
        self._opacity = 1.0
        if self._diode_triangle is None:
            return None
        return self._diode_triangle.animate.set_fill(opacity=1.0, **anim_args).build()

    @mn.override_animate(extinguish)
    def __animate_extinguish(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation | None:
        if anim_args is None:
            anim_args = {}
        self._opacity = 0.0
        if self._diode_triangle is None:
            return None
        return self._diode_triangle.animate.set_fill(opacity=0.0, **anim_args).build()


class Photodiode(Diode):
    """Circuit symbol for a photodiode."""

    def _construct(self) -> None:  # type: ignore[override]
        super()._construct()

        top_left = self._body.get_corner(mn.UL)
        right = self._body.get_right()
        perp_direction = mn.normalize(right - top_left)
        perp_length = np.linalg.norm(top_left - right)
        arrow_direction = np.cross(perp_direction, mn.IN)

        arrow_length = 0.55 * perp_length

        for alpha in [0.15, 0.35]:
            arrow_end = (
                top_left + alpha * perp_direction + 0.15 * perp_length * arrow_direction
            )
            arrow_start = arrow_end + arrow_length * arrow_direction

            self._body.add(
                mn.Arrow(
                    start=arrow_start,
                    end=arrow_end,
                    buff=0,
                    tip_length=config_eng.symbol.arrow_tip_length,
                    stroke_width=config_eng.symbol.arrow_stroke_width,
                    color=self.stroke_color,
                    stroke_opacity=self.stroke_opacity,
                    fill_opacity=self.stroke_opacity,
                )
            )


class SchottkyDiode(Diode):
    """Circuit symbol for a Schottky diode."""

    def _construct(self) -> None:  # type: ignore[override]
        super()._construct(draw_line=False)

        top = self._body.get_corner(mn.UR)
        bottom = self._body.get_corner(mn.DR)
        height = np.linalg.norm(bottom - top)
        side_length = 0.2 * height

        line = (
            mn.VMobject()
            .match_style(self)
            .set_fill(opacity=0)
            .set_points_as_corners(
                [
                    top + side_length * mn.DR,
                    top + side_length * mn.RIGHT,
                    top,
                    bottom,
                    bottom + side_length * mn.LEFT,
                    bottom + side_length * mn.UL,
                ]
            )
        )
        self._body.add(line)


class TunnelDiode(Diode):
    """Circuit symbol for a tunnel diode."""

    def _construct(self) -> None:  # type: ignore[override]
        super()._construct(draw_line=False)

        top = self._body.get_corner(mn.UR)
        bottom = self._body.get_corner(mn.DR)
        height = np.linalg.norm(bottom - top)
        side_length = 0.2 * height

        line = (
            mn.VMobject()
            .match_style(self)
            .set_fill(opacity=0)
            .set_points_as_corners(
                [
                    top + side_length * mn.LEFT,
                    top,
                    bottom,
                    bottom + side_length * mn.LEFT,
                ]
            )
        )
        self._body.add(line)


class ZenerDiode(Diode):
    """Circuit symbol for a Zener diode."""

    def _construct(self) -> None:  # type: ignore[override]
        super()._construct(draw_line=False)

        top = self._body.get_corner(mn.UR)
        bottom = self._body.get_corner(mn.DR)
        height = np.linalg.norm(bottom - top)
        offset = 0.2 * height * mn.rotate_vector(mn.UP, angle=60 * mn.DEGREES)

        line = (
            mn.VMobject()
            .match_style(self)
            .set_fill(opacity=0)
            .set_points_as_corners(
                [
                    bottom - offset,
                    bottom,
                    top,
                    top + offset,
                ]
            )
        )
        self._body.add(line)
