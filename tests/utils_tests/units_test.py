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
    PETA,
    PICO,
    QUECTO,
    QUETTA,
    RONNA,
    RONTO,
    TERA,
    VOLT,
    WATT,
    YOCTO,
    YOTTA,
    ZEPTO,
    ZETTA,
    Unit,
    UnitSequence,
    Value,
)


def test_unit_multiplication() -> None:
    assert UnitSequence([VOLT, AMP]) == VOLT * AMP


def test_unit_multiplication_cascading() -> None:
    assert UnitSequence([VOLT, AMP, COULOMB]) == VOLT * AMP * COULOMB


def test_unit_division() -> None:
    assert UnitSequence([VOLT, Unit(AMP.symbol, -1)]) == VOLT / AMP


def test_unit_division_cascading() -> None:
    assert (
        UnitSequence(
            [
                VOLT,
                Unit(AMP.symbol, -1),
                Unit(COULOMB.symbol, -1),
            ]
        )
        == VOLT / AMP / COULOMB
    )


def test_unit_power() -> None:
    assert Unit(VOLT.symbol, 2) == VOLT**2


def test_unit_power_prefix_does_not_power() -> None:
    assert KILO**2 == KILO


def test_unit_multiply_to_value() -> None:
    assert Value(3, UnitSequence([VOLT])) == 3 * VOLT


def test_unit_divide_to_value() -> None:
    assert Value(3, UnitSequence([Unit(VOLT.symbol, -1)])) == 3 / VOLT


def test_units_multiplication() -> None:
    assert UnitSequence([VOLT, AMP, COULOMB, FARAD]) == (VOLT * AMP) * (COULOMB * FARAD)


def test_units_division() -> None:
    assert UnitSequence(
        [
            VOLT,
            AMP,
            Unit(COULOMB.symbol, -1),
            Unit(FARAD.symbol, -1),
        ]
    ) == (VOLT * AMP) / (COULOMB * FARAD)


def test_units_division_does_not_change_prefix_exponent() -> None:
    assert UnitSequence([VOLT, MILLI, Unit(AMP.symbol, -1)]) == VOLT / (MILLI * AMP)


def test_units_multiply_to_value() -> None:
    assert Value(3, UnitSequence([VOLT, AMP])) == 3 * (VOLT * AMP)


def test_units_divide_to_value() -> None:
    assert Value(
        3,
        UnitSequence(
            [
                Unit(VOLT.symbol, -1),
                Unit(AMP.symbol, -1),
            ]
        ),
    ) == 3 / (VOLT * AMP)


def test_unit_multiply_with_units() -> None:
    assert UnitSequence([VOLT, AMP, COULOMB]) == VOLT * (AMP * COULOMB)
    assert UnitSequence([VOLT, AMP, COULOMB]) == (VOLT * AMP) * COULOMB


def test_unit_divide_with_units() -> None:
    assert UnitSequence(
        [
            VOLT,
            Unit(AMP.symbol, -1),
            Unit(COULOMB.symbol, -1),
        ]
    ) == VOLT / (AMP * COULOMB)
    assert (
        UnitSequence(
            [
                VOLT,
                AMP,
                Unit(COULOMB.symbol, -1),
            ]
        )
        == (VOLT * AMP) / COULOMB
    )


def test_combined_expression() -> None:
    assert Value(
        7.54, UnitSequence([KILO, WATT, HOUR, MEGA, Unit(HENRY.symbol, -2)])
    ) == 7.54 * KILO * WATT * HOUR / (MEGA * HENRY**2)


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
