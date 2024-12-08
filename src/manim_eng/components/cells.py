"""Component symbols of cells (a.k.a. batteries)."""

from typing import Any

import manim as mn

from manim_eng import config_eng
from manim_eng.components.base.source import VoltageSourceBase
from manim_eng.components.base.terminal import Terminal

__all__ = ["Battery", "Cell", "Cells", "DoubleCell", "QuadrupleCell", "TripleCell"]


class Cells(VoltageSourceBase):
    """Circuit symbol for a cell set with an arbitrary number of cells.

    Parameters
    ----------
    n : int
        Number of cells.
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(self, n: int, voltage: str | None = None, **kwargs: Any) -> None:
        self.num_cells = n

        self.__plate_half_gap = config_eng.symbol.plate_gap / 2
        self.__half_width = (2 * n - 1) * self.__plate_half_gap

        super().__init__(
            arrow=False,
            voltage=voltage,
            left=Terminal(
                position=mn.LEFT * self.__half_width,
                direction=mn.LEFT,
            ),
            right=Terminal(
                position=mn.RIGHT * self.__half_width,
                direction=mn.RIGHT,
            ),
            **kwargs,
        )

    def _construct(self) -> None:
        super()._construct()

        long_plate_half_height = config_eng.symbol.plate_height / 2
        short_plate_half_height = long_plate_half_height / 2

        for cell_index in range(self.num_cells):
            short_x = -self.__half_width + 4 * cell_index * self.__plate_half_gap

            short_plate_base = short_x * mn.RIGHT + (short_plate_half_height) * mn.DOWN
            long_plate_base = (
                short_x + 2 * self.__plate_half_gap
            ) * mn.RIGHT + long_plate_half_height * mn.DOWN

            short_plate = mn.Line(
                start=short_plate_base,
                end=short_plate_base + 2 * short_plate_half_height * mn.UP,
                stroke_width=config_eng.symbol.component_stroke_width,
            ).match_style(self)
            long_plate = mn.Line(
                start=long_plate_base,
                end=long_plate_base + 2 * long_plate_half_height * mn.UP,
                stroke_width=config_eng.symbol.component_stroke_width,
            ).match_style(self)

            self._body.add(short_plate, long_plate)


class Cell(Cells):
    """Circuit symbol for a single cell.

    Parameters
    ----------
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(n=1, voltage=voltage, **kwargs)


class DoubleCell(Cells):
    """Circuit symbol for a double cell (often used to represent a battery).

    Parameters
    ----------
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(n=2, voltage=voltage, **kwargs)


Battery = DoubleCell


class TripleCell(Cells):
    """Circuit symbol for a triple cell.

    Parameters
    ----------
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(n=3, voltage=voltage, **kwargs)


class QuadrupleCell(Cells):
    """Circuit symbol for a quadruple cell.

    Parameters
    ----------
    voltage : str | None
        Voltage label to set on creation, if desired. Takes a TeX math mode string.
    """

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(n=4, voltage=voltage, **kwargs)
