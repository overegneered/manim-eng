"""Tests for CurrentArrow set/clear/flip_direction behaviour."""

import manim as mn

from manim_eng.circuits.current import CurrentArrow


def _make_arrow(**kwargs: object) -> CurrentArrow:
    parent = mn.Line(mn.LEFT * 2, mn.RIGHT * 2)
    return CurrentArrow(parent, **kwargs)  # type: ignore[arg-type]


def test_current_arrow_starts_invisible() -> None:
    arrow = _make_arrow()

    assert arrow._triangle not in arrow.submobjects


def test_set_with_label_makes_arrow_visible() -> None:
    arrow = _make_arrow()

    arrow.set(label="I")

    assert arrow._triangle in arrow.submobjects


def test_set_with_label_updates_label_text() -> None:
    arrow = _make_arrow()

    arrow.set(label="I")

    assert arrow._label.tex_strings is not None
    assert arrow._label.tex_strings[0] == "I"


def test_set_without_label_on_invisible_arrow_does_not_make_it_visible() -> None:
    arrow = _make_arrow()

    arrow.set()

    assert arrow._triangle not in arrow.submobjects


def test_clear_on_visible_arrow_makes_it_not_visible() -> None:
    arrow = _make_arrow(label="I")

    arrow.clear()

    assert arrow._triangle not in arrow.submobjects


def test_flip_direction_toggles_invert_flag() -> None:
    arrow = _make_arrow()
    original_invert = arrow._invert

    arrow.flip_direction()

    assert arrow._invert is not original_invert


def test_flip_direction_twice_restores_original_state() -> None:
    arrow = _make_arrow()
    original_invert = arrow._invert
    original_alpha = arrow._alpha

    arrow.flip_direction()
    arrow.flip_direction()

    assert arrow._invert == original_invert
    assert arrow._alpha == original_alpha


def test_set_alpha_updates_alpha() -> None:
    expected_alpha = 0.3
    arrow = _make_arrow()

    arrow.set(alpha=expected_alpha)

    assert arrow._alpha == expected_alpha
