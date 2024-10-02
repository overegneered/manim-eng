"""Cell components (a.k.a. batteries)."""

from typing import Any

import manim as mn

from manim_eng import config_eng
from manim_eng.components.base.source import VoltageSourceBase
from manim_eng.components.base.terminal import Terminal

__all__ = ["Cells", "Cell", "DoubleCell", "TripleCell", "QuadrupleCell", "Battery"]


class Cells(VoltageSourceBase):
    """Cell component with arbitrary number of cells.

    Parameters
    ----------
    n : int
        Number of cells.
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(self, n: int, voltage: str | None = None, **kwargs: Any) -> None:
        self.num_cells = n

        self.plate_half_gap = config_eng.symbol.bipole_width / 12
        self.long_plate_half_height = 5 * self.plate_half_gap
        self.half_width = (2 * n - 1) * self.plate_half_gap

        super().__init__(
            arrow=False,
            voltage=voltage,
            left=Terminal(
                position=mn.LEFT * self.half_width,
                direction=mn.LEFT,
            ),
            right=Terminal(
                position=mn.RIGHT * self.half_width,
                direction=mn.RIGHT,
            ),
            **kwargs,
        )

    def _construct(self) -> None:
        super()._construct()

        short_plate_half_height = self.long_plate_half_height / 2

        for cell_index in range(self.num_cells):
            short_x = -self.half_width + 4 * cell_index * self.plate_half_gap
            short_plate_base = (short_x) * mn.RIGHT + (
                short_plate_half_height
            ) * mn.DOWN
            long_plate_base = (
                short_x + 2 * self.plate_half_gap
            ) * mn.RIGHT + self.long_plate_half_height * mn.DOWN
            short_plate = mn.Line(
                start=short_plate_base,
                end=short_plate_base + 2 * short_plate_half_height * mn.UP,
                stroke_width=config_eng.symbol.component_stroke_width,
            )
            long_plate = mn.Line(
                start=long_plate_base,
                end=long_plate_base + 2 * self.long_plate_half_height * mn.UP,
                stroke_width=config_eng.symbol.component_stroke_width,
            )
            self._body.add(short_plate, long_plate)


class Cell(Cells):
    """Cell component with a single cell.

    Parameters
    ----------
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(n=1, voltage=voltage, **kwargs)


class DoubleCell(Cells):
    """Cell component with two cells.

    Parameters
    ----------
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(n=2, voltage=voltage, **kwargs)


Battery = DoubleCell


class TripleCell(Cells):
    """Cell component with three cells.

    Parameters
    ----------
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(n=3, voltage=voltage, **kwargs)


class QuadrupleCell(Cells):
    """Cell component with four cells.

    Parameters
    ----------
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(n=4, voltage=voltage, **kwargs)
