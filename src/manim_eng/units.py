r"""Unit definitions and surrounding Value system.

A quick note on what this module does *not* do: it does *not* set out a complete unit
system, and you will experience issues if you use it that way.

This system is designed purely for the ergonomic specification of units of a quantity at
display time, and because of this, it is designed to precisely mirror the form of the
expression as it is written in code. The below highlights a particular quirk of this.

>>> 1 / (KILO * VOLT) == 1 * KILO / VOLT
True

This is because the system stores units as they would be *written*, and you would write
:math:`\mathrm{1 / kV = 1 kV^{-1}}` and not :math:`\mathrm{1 k^{-1} V^{-1}}`.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

__all__ = [
    "Unit",
    "Value",
    "E",
    "VOLT",
    "AMP",
    "OHM",
    "FARAD",
    "HENRY",
    "COULOMB",
    "SECOND",
    "MINUTE",
    "HOUR",
    "HERTZ",
    "RADIAN",
    "JOULE",
    "WATT",
    "DECIBEL",
    "QUECTO",
    "RONTO",
    "YOCTO",
    "ZEPTO",
    "ATTO",
    "FEMTO",
    "PICO",
    "NANO",
    "MICRO",
    "MILLI",
    "KILO",
    "MEGA",
    "GIGA",
    "TERA",
    "PETA",
    "EXA",
    "ZETTA",
    "YOTTA",
    "RONNA",
    "QUETTA",
]


class Unit:
    """An SI unit or prefix.

    Parameters
    ----------
    symbol : str
        The symbol of the unit. For metres this would be 'm'.
    latex : str, optional
        The latex math mode code to present the unit symbol. If not given, defaults to
        ``symbol``.
    exponent : int | float, optional
        The exponent of the unit (e.g. 2 for :math:`m^{2}`). Defaults to 1 if
        unspecified.
    prefix : bool, optional
        Whether the symbol is that of a prefix (e.g. 'k' for 'kilo') or that of a unit.
        Defaults to ``False`` if unspecified.
    """

    def __init__(
        self,
        symbol: str,
        latex: str | None = None,
        exponent: int | float = 1,
        prefix: bool = False,
    ):
        self.symbol = symbol
        self.latex = latex if latex is not None else symbol
        self.exponent = exponent
        self.prefix = prefix

    def to_latex(self) -> str:
        """Return a LaTeX math mode string representation of the unit."""
        if self.exponent == 1:
            return self.latex
        return f"{self.latex}^{{{self.exponent}}}"

    def __mul__(self, other: Unit | UnitSequence) -> UnitSequence:
        """Create a UnitSequence from this Unit and another Unit(Sequence)."""
        if isinstance(other, Unit):
            return UnitSequence([self]) * UnitSequence([other])
        if isinstance(other, UnitSequence):
            return UnitSequence([self, *other.units])
        return NotImplemented

    def __rmul__(self, other: int | float) -> Value:
        """Create a Value with a value of other and this Unit as its unit."""
        if isinstance(other, int | float):
            return other * UnitSequence([self])
        return NotImplemented

    def __truediv__(self, other: Unit | UnitSequence) -> UnitSequence:
        """Create a UnitSequence from this Unit and one over another Unit(Sequence)."""
        if isinstance(other, Unit):
            return UnitSequence([self]) / UnitSequence([other])
        if isinstance(other, UnitSequence):
            return UnitSequence([self]) / other
        return NotImplemented

    def __rtruediv__(self, other: int | float) -> Value:
        """Create a Value with a value of other the inverse of this Unit as its unit."""
        if isinstance(other, int | float):
            return other / UnitSequence([self])
        return NotImplemented

    def __pow__(self, exponent: int | float) -> Unit:
        """Set the exponent of the unit."""
        if isinstance(exponent, int | float):
            return Unit(
                self.symbol,
                exponent=self.exponent * exponent if not self.prefix else 1,
                prefix=self.prefix,
            )
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        """Check for equality between two units."""
        if isinstance(other, Unit):
            return (
                self.symbol == other.symbol
                and self.exponent == other.exponent
                and self.prefix == other.prefix
            )
        return NotImplemented

    def __repr__(self) -> str:
        """Return a string representation of the unit."""
        if self.exponent == 1:
            return self.symbol
        return f"{self.symbol}^{self.exponent}"


class E(Unit):
    """Unit representing scientific notation. Printed as '×10^{exponent}'.

    Parameters
    ----------
    exponent: int
        The exponent of the '10'.
    """

    def __init__(self, exponent: int) -> None:
        super().__init__("×10", latex=r"\times 10", exponent=exponent)

    def to_latex(self) -> str:
        """Return a LaTeX math mode string representation of scientific notation."""
        return f"{self.latex}^{{{self.exponent}}}"

    def __repr__(self) -> str:
        """Return a string representation of scientific notation."""
        return f"{self.symbol}^{self.exponent}"


class UnitSequence:
    r"""A sequence of individual units.

    This should be considered an internal implementation type, and is not intended for
    external use.

    Parameters
    ----------
    units : Sequence[Unit]
        An (ordered) sequence of Unit that form the set of units.

    Notes
    -----
    ``units``  represent how a unit set would be *written*, so prefixes never have
    exponents. For example, :math:`1 \mathrm{V s^{-1}}` would be
    [k, :math:`\mathrm{s^{-1}}`].
    """

    def __init__(self, units: Sequence[Unit]) -> None:
        self.units = units

    def to_latex(self) -> str:
        """Return a LaTeX math mode string representation of the unit."""
        rm_internal = ""
        for unit in self.units:
            rm_internal += unit.to_latex()
            if not unit.prefix:
                rm_internal += r"\,"
        rm_internal = rm_internal.rstrip(r"\,")
        return rf"\mathrm{{{rm_internal}}}"

    def __mul__(self, other: UnitSequence | Unit) -> UnitSequence:
        """Append the RHS units to the unit sequence."""
        if isinstance(other, UnitSequence):
            return UnitSequence([*self.units, *other.units])
        if isinstance(other, Unit):
            return UnitSequence([*self.units, other])
        return NotImplemented

    def __rmul__(self, other: int | float) -> Value:
        """Create a Value with value of other and units of this sequence."""
        if isinstance(other, int | float):
            return Value(other, self)
        return NotImplemented

    def __truediv__(self, other: UnitSequence | Unit) -> UnitSequence:
        """Append the RHS units to the unit sequence with negated exponent."""
        if isinstance(other, UnitSequence):
            other_units = []
            for unit in other.units:
                other_units.append(unit**-1)
            return self * UnitSequence(other_units)
        if isinstance(other, Unit):
            return self / UnitSequence([other])
        return NotImplemented

    def __rtruediv__(self, other: int | float) -> Value:
        """Create a Value with value of other and one over the units of this sequence.

        Parameters
        ----------
        other : int | float
            The numerical value to assign to the Value instance.

        Returns
        -------
        Value
            A Value with numerical value ``other`` and the units of this instance with
            the exponents negated.
        """
        if isinstance(other, int | float):
            units = []
            for unit in self.units:
                units.append(unit**-1)
            return Value(other, UnitSequence(units))
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        """Check for equality with another Units instance."""
        if isinstance(other, UnitSequence):
            return self.units == other.units
        return NotImplemented

    def __repr__(self) -> str:
        """Return a string representation of the unit sequence."""
        to_return = ""
        for unit in self.units:
            to_return += f"{unit}"
            if not unit.prefix:
                to_return += " "
        return to_return.rstrip()


VOLT = Unit("V")
AMP = Unit("A")
OHM = Unit("Ω", r"\Omega")
FARAD = Unit("F")
HENRY = Unit("H")
COULOMB = Unit("C")

SECOND = Unit("s")
MINUTE = Unit("min")
HOUR = Unit("hr")
HERTZ = Unit("Hz")
RADIAN = Unit("rad")

JOULE = Unit("J")
WATT = Unit("W")
DECIBEL = Unit("dB")

QUETTA = Unit("Q", prefix=True)
RONNA = Unit("R", prefix=True)
YOTTA = Unit("Y", prefix=True)
ZETTA = Unit("Z", prefix=True)
EXA = Unit("E", prefix=True)
PETA = Unit("P", prefix=True)
TERA = Unit("T", prefix=True)
GIGA = Unit("G", prefix=True)
MEGA = Unit("M", prefix=True)
KILO = Unit("k", prefix=True)
MILLI = Unit("m", prefix=True)
MICRO = Unit("µ", prefix=True)
NANO = Unit("n", prefix=True)
PICO = Unit("p", prefix=True)
FEMTO = Unit("f", prefix=True)
ATTO = Unit("a", prefix=True)
ZEPTO = Unit("z", prefix=True)
YOCTO = Unit("y", prefix=True)
RONTO = Unit("r", prefix=True)
QUECTO = Unit("q", prefix=True)

standard_engineering_prefixes = [
    QUECTO,
    RONTO,
    YOCTO,
    ZEPTO,
    ATTO,
    FEMTO,
    PICO,
    NANO,
    MICRO,
    MILLI,
    None,
    KILO,
    MEGA,
    GIGA,
    TERA,
    PETA,
    EXA,
    ZETTA,
    YOTTA,
    RONNA,
    QUETTA,
]


class Value:
    """Representation of a quantity with units for display purposes.

    This is *not* a full unit system implementation, and should not be treated as such.
    It is designed purely for being passed to display functions for them to pretty-print
    values with units with an ergonomic interface for the user.

    This constructor should not be used directly, but rather a value should be
    constructed through the product of an integer or float with a (combination of)
    units.

    >>> 2 * KILO * VOLT
    2 kV

    Parameters
    ----------
    value : int | float
        The numerical value of the quantity.
    units : UnitSequence
        The units of the quantity.
    """

    def __init__(self, value: int | float, units: UnitSequence) -> None:
        self.value = value
        self.units = units

    def to_latex(self) -> str:
        """Return a LaTeX math mode string representation of the unit."""
        spacing = r"\," if not isinstance(self.units.units[0], E) else ""
        return rf"{self.value}{spacing}{self.units.to_latex()}"

    @staticmethod
    def to_si(number: int | float) -> Value:
        """Convert a number to a factor and an SI prefix.

        Will only consider the standard multiples of 1000 (so e.g. 'c' for 'centi' will
        never be output).

        Parameters
        ----------
        number : int | float
            The value to convert.

        Returns
        -------
        Value
            A ``Value`` with the new factor and the SI prefix as its only unit.
        """
        prefix_offset = int((np.log10(float(number)) // 3))
        factor = number / 10 ** (prefix_offset * 3)
        prefix_index = (len(standard_engineering_prefixes) // 2) + prefix_offset
        prefix = standard_engineering_prefixes[prefix_index]
        units = UnitSequence([prefix] if prefix is not None else [])
        return Value(factor, units)

    def __mul__(self, other: Unit | UnitSequence) -> Value:
        """Append the RHS units to the Value's units."""
        return Value(self.value, self.units * other)

    def __truediv__(self, other: Unit | UnitSequence) -> Value:
        """Append the RHS units (with negated exponent) to the Value's units.

        Prefixes will not have their exponent negated, see the ``UnitSequence``
        documentation.
        """
        return Value(self.value, self.units / other)

    def __eq__(self, other: object) -> bool:
        """Check for equality with another Value."""
        if isinstance(other, Value):
            return self.value == other.value and self.units == other.units
        return NotImplemented

    def __repr__(self) -> str:
        """Return a string representation of the value."""
        spacing = " " if not isinstance(self.units.units[0], E) else ""
        return f"{self.value}{spacing}{self.units}"
