"""Mandatory xkcd: https://xkcd.com/2818/.

The components (or aliases) of Randall Munroe's circuit symbols.
"""

from typing import Any, Sequence

import manim as mn

from manim_eng import config_eng
from manim_eng.components.base.source import VoltageSourceBase
from manim_eng.components.base.terminal import Terminal
from manim_eng.components.capacitors import Capacitor
from manim_eng.components.diodes import Photodiode
from manim_eng.components.monopoles import Earth
from manim_eng.components.switches import Switch

__all__ = [
    "Baertty",
    "Battttttttttttery",
    "CheckOutThisReallyCoolDiode",
    "Drawbridge",
    "Overpass",
    "PogoStick",
]


Drawbridge = Switch
Overpass = Capacitor
PogoStick = Earth
CheckOutThisReallyCoolDiode = Photodiode


class RandalMunroeSourceBase(VoltageSourceBase):
    """Base class for Randall Munroe's cell circuit symbols.

    Parameters
    ----------
    pattern : Sequence[bool]
        The pattern of long to short plates. ``True`` denotes long, ``False`` denotes
        short.
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(
        self, pattern: Sequence[bool], voltage: str | None = None, **kwargs: Any
    ) -> None:
        self.pattern = pattern
        self.__half_width = 0.5 * (len(pattern) - 1) * config_eng.symbol.plate_gap

        super().__init__(
            arrow=False,
            voltage=voltage,
            left=Terminal(
                position=self.__half_width * mn.LEFT,
                direction=mn.LEFT,
            ),
            right=Terminal(
                position=self.__half_width * mn.RIGHT,
                direction=mn.RIGHT,
            ),
            **kwargs,
        )

    def _construct(self) -> None:
        super()._construct()

        long_plate_half_height = config_eng.symbol.plate_height / 2
        short_plate_half_height = 0.5 * long_plate_half_height

        current_x = self.__half_width * mn.LEFT
        for long in self.pattern:
            half_height = long_plate_half_height if long else short_plate_half_height
            line = mn.Line(
                start=current_x + half_height * mn.DOWN,
                end=current_x + half_height * mn.UP,
            ).match_style(self)
            self._body.add(line)
            current_x += config_eng.symbol.plate_gap * mn.RIGHT


class Baertty(RandalMunroeSourceBase):
    """Circuit symbol for Randall Munroe's baertty.

    See https://xkcd.com/2818/.

    Parameters
    ----------
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            pattern=[False, False, True, True],
            voltage=voltage,
            **kwargs,
        )


class Battttttttttttery(RandalMunroeSourceBase):
    """Circuit symbol for Randall Munroe's battttttttttttery.

    See https://xkcd.com/2818/.

    Parameters
    ----------
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            pattern=[False, True] + [False] * 6 + [True],
            voltage=voltage,
            **kwargs,
        )
