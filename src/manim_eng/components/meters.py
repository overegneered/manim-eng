"""Defines all kinds of measurement devices (voltmeter, ammeter, etc.)."""

from typing import Any

import manim as mn

from manim_eng import config_eng
from manim_eng.components.base.bipole import SquareBipole
from manim_eng.components.base.terminal import Terminal


class MeterBase(SquareBipole):
    """
    Base class for electronic measurement devices (meters).

    Parameters
    ----------
    letter : str | None, optional
        A single character representing the type of measurement device (e.g., 'V' for
        voltmeter, 'A' for ammeter, 'Ω' for ohmmeter). If provided, the letter will be
        displayed in the center of the meter symbol. Default is None, in which case no
        letter is displayed.
    **kwargs : Any
        Additional keyword arguments passed to the parent SquareBipole class.
    """

    def __init__(self, letter: str | None = None, **kwargs: Any) -> None:
        self._letter = letter
        radius = 0.5 * config_eng.symbol.meter_diameter
        super().__init__(
            left=Terminal(position=radius * mn.LEFT, direction=mn.LEFT),
            right=Terminal(position=radius * mn.RIGHT, direction=mn.RIGHT),
            **kwargs,
        )

    def _construct(self) -> None:
        super()._construct()
        radius = 0.5 * config_eng.symbol.meter_diameter
        circle = mn.Circle(radius).match_style(self)
        self._body.add(circle)
        if self._letter is not None:
            letter = mn.Text(
                self._letter, font=config_eng.symbol.meter_font, weight=mn.BOLD
            ).scale_to_fit_height(circle.height * 0.5)
            self._body.add(letter)


class Voltmeter(MeterBase):
    """Circuit symbol for voltmeter."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(letter="V", **kwargs)


class Ammeter(MeterBase):
    """Circuit symbol for ammeter."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(letter="A", **kwargs)


class Galvanometer(MeterBase):
    """Circuit symbol for galvanometer."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(letter="G", **kwargs)


class Ohmmeter(MeterBase):
    """Circuit symbol for ohmmeter."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(letter="Ω", **kwargs)


class FrequencyMeter(MeterBase):
    """Circuit symbol for frequency meter."""

    def __init__(self, **kwargs: Any) -> None:
        try:
            super().__init__(letter="㎐", **kwargs)
        except Exception:
            # The font might not support unicode letter. Try two letter 'Hz' instead
            super().__init__(letter="Hz", **kwargs)
