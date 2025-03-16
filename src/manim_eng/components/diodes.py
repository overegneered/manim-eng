"""Component symbols of diodes."""

import manim as mn
import numpy as np

from manim_eng import config_eng
from manim_eng.components.base.bipole import SquareBipole
from manim_eng.components.base.terminal import Terminal

__all__ = ["LED", "Diode", "Photodiode", "SchottkyDiode", "TunnelDiode", "ZenerDiode"]


class Diode(SquareBipole):
    """Circuit symbol for a diode."""

    def _construct(self, draw_line: bool = True) -> None:
        """Construct a basic diode.

        Parameters
        ----------
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
            .shift((1 / 12) * mn.LEFT)
        )
        self._body.add(triangle)

        if draw_line:
            line = (
                mn.Line(
                    start=line_start + half_height * mn.DOWN,
                    end=line_start + half_height * mn.UP,
                )
                .match_style(self)
                .set_fill(opacity=0)
            )
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
    """Circuit symbol for an LED."""

    def _construct(self) -> None:  # type: ignore[override]
        super()._construct()

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
