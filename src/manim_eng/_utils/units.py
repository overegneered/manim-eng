import numpy as np

VOLT = "V"
AMP = "A"
OHM = "Ω"
FARAD = "F"
HENRY = "H"
COULOMB = "C"

SECOND = "s"
MINUTE = "min"
HOUR = "hr"
HERTZ = "Hz"

JOULE = "J"
WATT = "W"
DECIBEL = "dB"

QUETTA = "Q"
RONNA = "R"
YOTTA = "Y"
ZETTA = "Z"
EXA = "E"
PETA = "P"
TERA = "T"
GIGA = "G"
MEGA = "M"
KILO = "k"
MILLI = "m"
MICRO = "µ"
NANO = "n"
PICO = "p"
FEMTO = "f"
ATTO = "a"
ZEPTO = "z"
YOCTO = "y"
RONTO = "r"
QUECTO = "q"

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
    "",
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


def value_to_si(value: float) -> tuple[float, str]:
    """Convert a value to a SI prefix symbol and the new value that should precede it.

    Will only consider the standard multiples of 1000 (so e.g. 'c' for 'centi' will
    never be output).

    Parameters
    ----------
    value : float
        The value to convert.

    Returns
    -------
    tuple[float, str]
        A tuple containing the new value and the corresponding SI prefix. If no prefix
        is needed, the second element will be an empty string ``""``.
    """
    prefix_offset = int((np.log10(float(value)) // 3))
    prefix_index = (len(standard_engineering_prefixes) // 2) + prefix_offset
    prefix = standard_engineering_prefixes[prefix_index]
    new_value = value / 10 ** (prefix_offset * 3)
    return new_value, prefix
