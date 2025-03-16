"""manim-eng logo and implementation class."""

import manim as mn

from manim_eng.components.diodes import ZenerDiode
from manim_eng.components.resistors import Resistor
from manim_eng.components.sources import CurrentSource

__all__ = ["ManimEngLogo"]


class ManimEngLogoComponentArrangement(mn.VGroup):
    """Component arrangement for manim-eng's logo."""

    def __init__(self) -> None:
        super().__init__()

        isource = CurrentSource(
            color=mn.LOGO_GREEN, fill_color=mn.config.background_color, fill_opacity=1
        ).shift(0.5 * mn.LEFT)
        resistor = Resistor(
            color=mn.LOGO_BLUE, fill_color=mn.config.background_color, fill_opacity=1
        ).shift(0.315 * mn.UP)
        diode = (
            ZenerDiode(color=mn.LOGO_RED).rotate(90 * mn.DEGREES).shift(0.5 * mn.RIGHT)
        )

        self.add(diode, resistor, isource)


class ManimEngLogo(ManimEngLogoComponentArrangement):
    """manim-eng logo.

    Parameters
    ----------
    dark_theme : bool, optional
        Whether to adapt the logo for a dark theme (default) or a light theme.
    """

    def __init__(self, dark_theme: bool = True) -> None:
        super().__init__()

        text = mn.Tex(
            r"\textsf{manim-\textbf{eng}}",
            font_size=80,
            z_index=1,
            color=mn.LOGO_WHITE if dark_theme else mn.LOGO_BLACK,
        ).align_to(0.55 * mn.LEFT + 0.05 * mn.UP, mn.DR)

        self.add(text)
        self.shift(-self.get_center())
