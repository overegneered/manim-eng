from __future__ import annotations

import dataclasses as dc

import numpy as np


@dc.dataclass
class Unit:
    symbol: str
    exponent: int | float = 1
    prefix: bool = False

    def __mul__(self, other: Unit) -> Units:
        if isinstance(other, Unit):
            return Units([self]) * Units([other])
        if isinstance(other, Units):
            return Units([self, *other.units])
        return NotImplemented

    def __rmul__(self, other: int | float) -> Value:
        if isinstance(other, int | float):
            return other * Units([self])
        return NotImplemented

    def __truediv__(self, other: Unit) -> Units:
        if isinstance(other, Unit):
            return Units([self]) / Units([other])
        if isinstance(other, Units):
            return Units([self]) / other
        return NotImplemented

    def __rtruediv__(self, other: int | float) -> Value:
        if isinstance(other, int | float):
            return other / Units([self])
        return NotImplemented

    def __pow__(self, exponent: int | float) -> Unit:
        if isinstance(exponent, int | float):
            return Unit(
                self.symbol,
                self.exponent * exponent if not self.prefix else 1,
                self.prefix,
            )
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Unit):
            return (
                self.symbol == other.symbol
                and self.exponent == other.exponent
                and self.prefix == other.prefix
            )
        return NotImplemented

    def __repr__(self) -> str:
        if self.exponent == 1:
            return f"{self.symbol}"
        return f"{self.symbol}^{self.exponent}"


class Units:
    def __init__(self, units: list[Unit]) -> None:
        self.units = units

    def __mul__(self, other: Units | Unit) -> Units:
        if isinstance(other, Units):
            return Units([*self.units, *other.units])
        if isinstance(other, Unit):
            return Units([*self.units, other])
        return NotImplemented

    def __rmul__(self, other: Unit | int | float) -> Value:
        if isinstance(other, int | float):
            return Value(other, self)
        return NotImplemented

    def __truediv__(self, other: Units | Unit) -> Units:
        if isinstance(other, Units):
            other_units = []
            for unit in other.units:
                other_units.append(unit**-1)
            return self * Units(other_units)
        if isinstance(other, Unit):
            return self / Units([other])
        return NotImplemented

    def __rtruediv__(self, other: Unit | int | float) -> Value:
        if isinstance(other, int | float):
            units = []
            for unit in self.units:
                units.append(unit**-1)
            return Value(other, Units(units))
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Units):
            return self.units == other.units
        return NotImplemented

    def __repr__(self) -> str:
        to_return = ""
        for unit in self.units:
            to_return += f"{unit}"
            if not unit.prefix:
                to_return += " "
        to_return.rstrip()
        return to_return


VOLT = Unit("V")
AMP = Unit("A")
OHM = Unit("Ω")
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
    def __init__(self, value: int | float, units: Units) -> None:
        self.value = value
        self.units = units

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
        units = Units([prefix] if prefix is not None else [])
        return Value(factor, units)

    def __mul__(self, other: Unit | Units) -> Value:
        return Value(self.value, self.units * other)

    def __truediv__(self, other: Unit | Units) -> Value:
        return Value(self.value, self.units / other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Value):
            return self.value == other.value and self.units == other.units
        return NotImplemented

    def __repr__(self) -> str:
        return f"{self.value} {self.units}"
