import numpy as np
import pytest
from manim_eng.units import (
    AMP,
    ATTO,
    COULOMB,
    EXA,
    FARAD,
    FEMTO,
    GIGA,
    HENRY,
    HOUR,
    KILO,
    MEGA,
    MICRO,
    MILLI,
    NANO,
    OHM,
    PETA,
    PICO,
    QUECTO,
    QUETTA,
    RONNA,
    RONTO,
    SECOND,
    TERA,
    VOLT,
    WATT,
    YOCTO,
    YOTTA,
    ZEPTO,
    ZETTA,
    E,
    Unit,
    UnitSequence,
    Value,
)


def test_unit_multiplication() -> None:
    assert UnitSequence([VOLT, AMP]) == VOLT * AMP


def test_unit_multiplication_cascading() -> None:
    assert UnitSequence([VOLT, AMP, COULOMB]) == VOLT * AMP * COULOMB


def test_unit_division() -> None:
    assert UnitSequence([VOLT, Unit(AMP.symbol, exponent=-1)]) == VOLT / AMP


def test_unit_division_cascading() -> None:
    assert (
        UnitSequence(
            [
                VOLT,
                Unit(AMP.symbol, exponent=-1),
                Unit(COULOMB.symbol, exponent=-1),
            ]
        )
        == VOLT / AMP / COULOMB
    )


def test_unit_power() -> None:
    assert Unit(VOLT.symbol, exponent=2) == VOLT**2


def test_unit_power_prefix_does_not_power() -> None:
    assert KILO**2 == KILO


def test_unit_multiply_to_value() -> None:
    assert Value(3, UnitSequence([VOLT])) == 3 * VOLT


def test_unit_divide_to_value() -> None:
    assert Value(3, UnitSequence([Unit(VOLT.symbol, exponent=-1)])) == 3 / VOLT


def test_unit_sequence_multiplication() -> None:
    assert UnitSequence([VOLT, AMP, COULOMB, FARAD]) == (VOLT * AMP) * (COULOMB * FARAD)


def test_unit_sequence_division() -> None:
    assert UnitSequence(
        [
            VOLT,
            AMP,
            Unit(COULOMB.symbol, exponent=-1),
            Unit(FARAD.symbol, exponent=-1),
        ]
    ) == (VOLT * AMP) / (COULOMB * FARAD)


def test_unit_sequence_division_does_not_change_prefix_exponent() -> None:
    assert UnitSequence([VOLT, MILLI, Unit(AMP.symbol, exponent=-1)]) == VOLT / (
        MILLI * AMP
    )


def test_unit_sequence_multiply_to_value() -> None:
    assert Value(3, UnitSequence([VOLT, AMP])) == 3 * (VOLT * AMP)


def test_unit_sequence_divide_to_value() -> None:
    assert Value(
        3,
        UnitSequence(
            [
                Unit(VOLT.symbol, exponent=-1),
                Unit(AMP.symbol, exponent=-1),
            ]
        ),
    ) == 3 / (VOLT * AMP)


def test_unit_multiply_with_unit_sequence() -> None:
    assert UnitSequence([VOLT, AMP, COULOMB]) == VOLT * (AMP * COULOMB)
    assert UnitSequence([VOLT, AMP, COULOMB]) == (VOLT * AMP) * COULOMB


def test_unit_divide_with_unit_sequence() -> None:
    assert UnitSequence(
        [
            VOLT,
            Unit(AMP.symbol, exponent=-1),
            Unit(COULOMB.symbol, exponent=-1),
        ]
    ) == VOLT / (AMP * COULOMB)
    assert (
        UnitSequence(
            [
                VOLT,
                AMP,
                Unit(COULOMB.symbol, exponent=-1),
            ]
        )
        == (VOLT * AMP) / COULOMB
    )


def test_combined_expression() -> None:
    assert Value(
        7.54, UnitSequence([KILO, WATT, HOUR, MEGA, Unit(HENRY.symbol, exponent=-2)])
    ) == 7.54 * KILO * WATT * HOUR / (MEGA * HENRY**2)


def test_unit_takes_symbol_if_no_latex_specified() -> None:
    unit = Unit("m")

    assert unit.latex == "m"


def test_unit_takes_latex_if_latex_specified() -> None:
    unit = Unit("Ω", r"\Omega")

    assert unit.latex == r"\Omega"


@pytest.mark.parametrize(
    ("unit", "expected_latex"),
    [
        pytest.param(VOLT, "V", id="normal"),
        pytest.param(VOLT**2, "V^{2}", id="positive exponent"),
        pytest.param(VOLT**-4, "V^{-4}", id="negative exponent"),
        pytest.param(OHM, r"\Omega", id="latex symbol"),
    ],
)
def test_unit_to_latex(unit: Unit, expected_latex: str) -> None:
    actual_latex = unit.to_latex()

    assert actual_latex == expected_latex


@pytest.mark.parametrize(
    ("exponent", "expected_latex"),
    [
        pytest.param(5, r"\times 10^{5}", id="standard exponent"),
        pytest.param(1, r"\times 10^{1}", id="exponent of 1 is printed"),
        pytest.param(-1, r"\times 10^{-1}", id="negative exponent"),
    ],
)
def test_e_to_latex(exponent: int, expected_latex: str) -> None:
    actual_latex = E(exponent).to_latex()

    assert actual_latex == expected_latex


@pytest.mark.parametrize(
    ("exponent", "expected_string"),
    [
        pytest.param(5, r"×10^5", id="standard exponent"),
        pytest.param(1, r"×10^1", id="exponent of 1 is printed"),
        pytest.param(-1, r"×10^-1", id="negative exponent"),
    ],
)
def test_e_repr(exponent: int, expected_string: str) -> None:
    actual_string = f"{E(exponent)}"

    assert actual_string == expected_string


def test_value_with_e_first_has_no_spacing_in_latex() -> None:
    actual_latex = (3.4 * E(3) * VOLT).to_latex()

    assert actual_latex == r"3.4\mathrm{\times 10^{3}\,V}"


def test_value_with_e_first_has_no_spacing_in_repr() -> None:
    actual_repr = f"{(3.4 * E(3) * VOLT)}"

    assert actual_repr == r"3.4×10^3 V"


@pytest.mark.parametrize(
    ("unit_sequence", "expected_latex"),
    [
        pytest.param(VOLT * AMP, r"V\,A", id="two units"),
        pytest.param(KILO * VOLT, r"kV", id="prefix has no space"),
        pytest.param(VOLT**2 * AMP, r"V^{2}\,A", id="positive exponent"),
        pytest.param(VOLT * AMP**-4, r"V\,A^{-4}", id="negative exponent"),
        pytest.param(
            KILO * VOLT / (MILLI * AMP), r"kV\,mA^{-1}", id="multiple prefixes"
        ),
    ],
)
def test_unit_sequence_to_latex(
    unit_sequence: UnitSequence, expected_latex: str
) -> None:
    actual_latex = unit_sequence.to_latex()

    assert actual_latex == rf"\mathrm{{{expected_latex}}}"


@pytest.mark.parametrize(
    ("value", "expected_latex"),
    [
        pytest.param(2 * VOLT, r"2\,\mathrm{V}", id="single unit"),
        pytest.param(2 * KILO * VOLT, r"2\,\mathrm{kV}", id="unit with prefix"),
        pytest.param(
            3.14 / SECOND,
            r"3.14\,\mathrm{s^{-1}}",
            id="float with negative unit exponent",
        ),
        pytest.param(
            7.54 * KILO * WATT * HOUR / (MEGA * HENRY**2),
            r"7.54\,\mathrm{kW\,hr\,MH^{-2}}",
            id="altogether now!",
        ),
    ],
)
def test_value_to_latex(value: Value, expected_latex: str) -> None:
    actual_latex = value.to_latex()

    assert actual_latex == expected_latex


@pytest.mark.parametrize(
    ("number", "expected_value", "expected_prefix"),
    [
        pytest.param(1e-30, 1, [QUECTO], id="10^-30"),
        pytest.param(1e-29, 10, [QUECTO], id="10^-29"),
        pytest.param(1e-28, 100, [QUECTO], id="10^-28"),
        pytest.param(1e-27, 1, [RONTO], id="10^-27"),
        pytest.param(1e-26, 10, [RONTO], id="10^-26"),
        pytest.param(1e-25, 100, [RONTO], id="10^-25"),
        pytest.param(1e-24, 1, [YOCTO], id="10^-24"),
        pytest.param(1e-23, 10, [YOCTO], id="10^-23"),
        pytest.param(1e-22, 100, [YOCTO], id="10^-22"),
        pytest.param(1e-21, 1, [ZEPTO], id="10^-21"),
        pytest.param(1e-20, 10, [ZEPTO], id="10^-20"),
        pytest.param(1e-19, 100, [ZEPTO], id="10^-19"),
        pytest.param(1e-18, 1, [ATTO], id="10^-18"),
        pytest.param(1e-17, 10, [ATTO], id="10^-17"),
        pytest.param(1e-16, 100, [ATTO], id="10^-16"),
        pytest.param(1e-15, 1, [FEMTO], id="10^-15"),
        pytest.param(1e-14, 10, [FEMTO], id="10^-14"),
        pytest.param(1e-13, 100, [FEMTO], id="10^-13"),
        pytest.param(1e-12, 1, [PICO], id="10^-12"),
        pytest.param(1e-11, 10, [PICO], id="10^-11"),
        pytest.param(1e-10, 100, [PICO], id="10^-10"),
        pytest.param(1e-9, 1, [NANO], id="10^-9"),
        pytest.param(1e-8, 10, [NANO], id="10^-8"),
        pytest.param(1e-7, 100, [NANO], id="10^-7"),
        pytest.param(1e-6, 1, [MICRO], id="10^-6"),
        pytest.param(1e-5, 10, [MICRO], id="10^-5"),
        pytest.param(1e-4, 100, [MICRO], id="10^-4"),
        pytest.param(1e-3, 1, [MILLI], id="10^-3"),
        pytest.param(1e-2, 10, [MILLI], id="10^-2"),
        pytest.param(1e-1, 100, [MILLI], id="10^-1"),
        pytest.param(1e0, 1, [], id="10^0"),
        pytest.param(1e1, 10, [], id="10^1"),
        pytest.param(1e2, 100, [], id="10^2"),
        pytest.param(1e3, 1, [KILO], id="10^3"),
        pytest.param(1e4, 10, [KILO], id="10^4"),
        pytest.param(1e5, 100, [KILO], id="10^5"),
        pytest.param(1e6, 1, [MEGA], id="10^6"),
        pytest.param(1e7, 10, [MEGA], id="10^7"),
        pytest.param(1e8, 100, [MEGA], id="10^8"),
        pytest.param(1e9, 1, [GIGA], id="10^9"),
        pytest.param(1e10, 10, [GIGA], id="10^10"),
        pytest.param(1e11, 100, [GIGA], id="10^11"),
        pytest.param(1e12, 1, [TERA], id="10^12"),
        pytest.param(1e13, 10, [TERA], id="10^13"),
        pytest.param(1e14, 100, [TERA], id="10^14"),
        pytest.param(1e15, 1, [PETA], id="10^15"),
        pytest.param(1e16, 10, [PETA], id="10^16"),
        pytest.param(1e17, 100, [PETA], id="10^17"),
        pytest.param(1e18, 1, [EXA], id="10^18"),
        pytest.param(1e19, 10, [EXA], id="10^19"),
        pytest.param(1e20, 100, [EXA], id="10^20"),
        pytest.param(1e21, 1, [ZETTA], id="10^21"),
        pytest.param(1e22, 10, [ZETTA], id="10^22"),
        pytest.param(1e23, 100, [ZETTA], id="10^23"),
        pytest.param(1e24, 1, [YOTTA], id="10^24"),
        pytest.param(1e25, 10, [YOTTA], id="10^25"),
        pytest.param(1e26, 100, [YOTTA], id="10^26"),
        pytest.param(1e27, 1, [RONNA], id="10^27"),
        pytest.param(1e28, 10, [RONNA], id="10^28"),
        pytest.param(1e29, 100, [RONNA], id="10^29"),
        pytest.param(1e30, 1, [QUETTA], id="10^30"),
        pytest.param(1e31, 10, [QUETTA], id="10^31"),
        pytest.param(1e32, 100, [QUETTA], id="10^32"),
        pytest.param(5.7e5, 570, [KILO], id="57e5"),
        pytest.param(850, 850, [], id="850"),
    ],
)
def test_value_to_si(
    number: float, expected_value: float, expected_prefix: list[Unit]
) -> None:
    actual_value = Value.to_si(number)

    assert np.isclose(actual_value.value, expected_value)
    assert actual_value.units == UnitSequence(expected_prefix)
