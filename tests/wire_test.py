from collections.abc import Callable

import manim as mn
import pytest

from manim_eng import ManualWire, Wire
from manim_eng.components.base.pin import Pin


def test_wire_throws_value_error_if_pins_are_identical() -> None:
    pin = Pin(mn.ORIGIN, mn.LEFT)

    with pytest.raises(
        ValueError,
        match=r"`start` and `end` are identical\. "
        r"Wires must have different pins at each end\.",
    ):
        Wire(pin, pin)


def test_manual_wire_throws_value_error_if_pins_are_identical() -> None:
    pin = Pin(mn.ORIGIN, mn.LEFT)

    with pytest.raises(
        ValueError,
        match=r"`start` and `end` are identical\. "
        r"Wires must have different pins at each end\.",
    ):
        ManualWire(pin, pin, [])


# Helpers ==============================================================================

_CREATION_ANIM_FACTORIES: list[Callable[[Wire], mn.Animation]] = [
    mn.Create,
    mn.FadeIn,
    mn.Write,
    mn.DrawBorderThenFill,
    mn.GrowFromCenter,
    lambda w: mn.GrowFromPoint(w, point=mn.ORIGIN),
    lambda w: mn.GrowFromEdge(w, edge=mn.LEFT),
    mn.SpinInFromNothing,
    mn.SpiralIn,
]

_DESTRUCTION_ANIM_FACTORIES: list[Callable[[Wire], mn.Animation]] = [
    mn.Uncreate,
    mn.FadeOut,
    mn.Unwrite,
    mn.ShrinkToCenter,
]


# Initial state ========================================================================


def test_wire_is_hidden_on_construction(wire: Wire) -> None:
    assert wire.is_visible() is False


# Creation animations ==================================================================


@pytest.mark.parametrize("factory", _CREATION_ANIM_FACTORIES)
def test_creation_animation_sets_wire_visible_on_begin(
    wire: Wire, factory: Callable[[Wire], mn.Animation]
) -> None:
    anim = factory(wire)
    anim.begin()

    assert wire.is_visible() is True


@pytest.mark.parametrize("factory", _CREATION_ANIM_FACTORIES)
def test_wire_hidden_before_creation_animation_begins(
    wire: Wire, factory: Callable[[Wire], mn.Animation]
) -> None:
    _anim = factory(wire)

    assert wire.is_visible() is False


@pytest.mark.parametrize("factory", _CREATION_ANIM_FACTORIES)
def test_wire_remains_visible_after_creation_animation_finishes(
    wire: Wire, factory: Callable[[Wire], mn.Animation]
) -> None:
    anim = factory(wire)
    anim.begin()
    anim.finish()

    assert wire.is_visible() is True


# Destruction animations ===============================================================


@pytest.mark.parametrize("factory", _DESTRUCTION_ANIM_FACTORIES)
def test_destruction_animation_sets_wire_hidden_on_finish(
    wire: Wire, factory: Callable[[Wire], mn.Animation]
) -> None:
    wire._set_visible()
    anim = factory(wire)
    anim.begin()
    anim.finish()

    assert wire.is_visible() is False


@pytest.mark.parametrize("factory", _DESTRUCTION_ANIM_FACTORIES)
def test_wire_remains_visible_during_destruction_animation(
    wire: Wire, factory: Callable[[Wire], mn.Animation]
) -> None:
    wire._set_visible()
    anim = factory(wire)
    anim.begin()

    assert wire.is_visible() is True


# Dispatch produces correct visibility behaviour (end-to-end) ==========================


@pytest.mark.parametrize("factory", _CREATION_ANIM_FACTORIES)
def test_creation_animation_dispatch_produces_correct_visibility_behaviour(
    wire: Wire, factory: Callable[[Wire], mn.Animation]
) -> None:
    anim = factory(wire)
    anim.begin()

    assert wire.is_visible() is True


@pytest.mark.parametrize("factory", _DESTRUCTION_ANIM_FACTORIES)
def test_destruction_animation_dispatch_produces_correct_visibility_behaviour(
    wire: Wire, factory: Callable[[Wire], mn.Animation]
) -> None:
    wire._set_visible()
    anim = factory(wire)
    anim.begin()
    anim.finish()

    assert wire.is_visible() is False
