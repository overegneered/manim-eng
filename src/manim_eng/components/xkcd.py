"""Mandatory xkcd: https://xkcd.com/2818/.

The components (or aliases) of Randall Munroe's circuit symbols.
"""

from typing import Any

from manim_eng.components.base.xkcd import RandalMunroeSourceBase
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
