from typing import Callable

import manim as mn
import pytest

from manim_eng.implementation import WireBase

# --------------------------------------------------------------------------------------
# animation overrides
# --------------------------------------------------------------------------------------

_CREATION_ANIM_FACTORIES: list[Callable[[WireBase], mn.Animation]] = [
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

_DESTRUCTION_ANIM_FACTORIES: list[Callable[[WireBase], mn.Animation]] = [
    mn.Uncreate,
    mn.FadeOut,
    mn.Unwrite,
    mn.ShrinkToCenter,
]


def test_wire_is_hidden_on_construction(wire: WireBase) -> None:
    assert wire.is_visible() is False


# Creation animations ------------------------------------------------------------------


@pytest.mark.parametrize("factory", _CREATION_ANIM_FACTORIES)
def test_creation_animation_sets_wire_visible_on_begin(
    wire: WireBase, factory: Callable[[WireBase], mn.Animation]
) -> None:
    anim = factory(wire)
    anim.begin()

    assert wire.is_visible() is True


@pytest.mark.parametrize("factory", _CREATION_ANIM_FACTORIES)
def test_wire_hidden_before_creation_animation_begins(
    wire: WireBase, factory: Callable[[WireBase], mn.Animation]
) -> None:
    _anim = factory(wire)

    assert wire.is_visible() is False


@pytest.mark.parametrize("factory", _CREATION_ANIM_FACTORIES)
def test_wire_remains_visible_after_creation_animation_finishes(
    wire: WireBase, factory: Callable[[WireBase], mn.Animation]
) -> None:
    anim = factory(wire)
    anim.begin()
    anim.finish()

    assert wire.is_visible() is True


@pytest.mark.parametrize("factory", _CREATION_ANIM_FACTORIES)
def test_creation_animation_dispatch_produces_correct_visibility_behaviour(
    wire: WireBase, factory: Callable[[WireBase], mn.Animation]
) -> None:
    anim = factory(wire)
    anim.begin()

    assert wire.is_visible() is True


# Destruction animations ---------------------------------------------------------------


@pytest.mark.parametrize("factory", _DESTRUCTION_ANIM_FACTORIES)
def test_destruction_animation_sets_wire_hidden_on_finish(
    wire: WireBase, factory: Callable[[WireBase], mn.Animation]
) -> None:
    wire._set_visible()
    anim = factory(wire)
    anim.begin()
    anim.finish()

    assert wire.is_visible() is False


@pytest.mark.parametrize("factory", _DESTRUCTION_ANIM_FACTORIES)
def test_wire_remains_visible_during_destruction_animation(
    wire: WireBase, factory: Callable[[WireBase], mn.Animation]
) -> None:
    wire._set_visible()
    anim = factory(wire)
    anim.begin()

    assert wire.is_visible() is True


@pytest.mark.parametrize("factory", _DESTRUCTION_ANIM_FACTORIES)
def test_destruction_animation_dispatch_produces_correct_visibility_behaviour(
    wire: WireBase, factory: Callable[[WireBase], mn.Animation]
) -> None:
    wire._set_visible()
    anim = factory(wire)
    anim.begin()
    anim.finish()

    assert wire.is_visible() is False
