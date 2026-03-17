"""Tests for the Markable base class and RotateMarkable animation."""

from unittest import mock

import manim as mn
import numpy as np
import pytest

from manim_eng._base.anchor import Anchor
from manim_eng._base.mark import Mark
from manim_eng._base.markable import Markable, _RotateMarkable


class ConcreteMarkable(Markable):
    """Minimal concrete subclass of Markable for use as a test double."""


def make_mark() -> Mark:
    """Return a Mark with two mocked anchors at distinct positions."""
    anchor = mock.MagicMock(Anchor)
    anchor.pos = np.array([1.0, 0.0, 0.0])
    centre = mock.MagicMock(Anchor)
    centre.pos = np.array([0.0, 0.0, 0.0])
    return Mark(anchor, centre)


@pytest.fixture
def markable() -> ConcreteMarkable:
    return ConcreteMarkable()


@pytest.fixture
def plain_vmobject() -> mn.VMobject:
    return mn.VMobject()


@pytest.fixture
def mark() -> Mark:
    return make_mark()


@pytest.fixture
def child_markable() -> ConcreteMarkable:
    return ConcreteMarkable()


# add() routing ========================================================================


def test_add_vmobject_appears_in_submobjects(
    markable: ConcreteMarkable, plain_vmobject: mn.VMobject
) -> None:
    markable.add(plain_vmobject)

    assert plain_vmobject in markable.submobjects


def test_add_mark_appears_in_submobjects(
    markable: ConcreteMarkable, mark: Mark
) -> None:
    markable.add(mark)

    assert mark in markable.submobjects


def test_add_child_markable_appears_in_submobjects(
    markable: ConcreteMarkable, child_markable: ConcreteMarkable
) -> None:
    markable.add(child_markable)

    assert child_markable in markable.submobjects


# submobjects getter: ordering should be __rotate, __marks, __markables ================


def test_submobjects_order_rotate_then_marks_then_markables(
    markable: ConcreteMarkable,
    plain_vmobject: mn.VMobject,
    mark: Mark,
    child_markable: ConcreteMarkable,
) -> None:
    markable.add(plain_vmobject)
    markable.add(mark)
    markable.add(child_markable)

    subs = markable.submobjects
    rotate_idx = subs.index(plain_vmobject)
    mark_idx = subs.index(mark)
    markable_idx = subs.index(child_markable)

    assert rotate_idx < mark_idx < markable_idx


def test_submobjects_does_not_expose_internal_vgroups(
    markable: ConcreteMarkable,
    plain_vmobject: mn.VMobject,
    mark: Mark,
    child_markable: ConcreteMarkable,
) -> None:
    markable.add(plain_vmobject)
    markable.add(mark)
    markable.add(child_markable)

    known = (plain_vmobject, mark, child_markable)
    for sub in markable.submobjects:
        assert not (isinstance(sub, mn.VGroup) and sub not in known)


# add_to_back() routing ================================================================


def test_add_to_back_vmobject_appears_in_submobjects(
    markable: ConcreteMarkable, plain_vmobject: mn.VMobject
) -> None:
    markable.add_to_back(plain_vmobject)

    assert plain_vmobject in markable.submobjects


def test_add_to_back_mark_appears_in_submobjects(
    markable: ConcreteMarkable, mark: Mark
) -> None:
    markable.add_to_back(mark)

    assert mark in markable.submobjects


def test_add_to_back_child_markable_appears_in_submobjects(
    markable: ConcreteMarkable, child_markable: ConcreteMarkable
) -> None:
    markable.add_to_back(child_markable)

    assert child_markable in markable.submobjects


def test_add_to_back_vmobject_placed_before_existing(
    markable: ConcreteMarkable,
) -> None:
    first = mn.VMobject()
    second = mn.VMobject()
    markable.add(first)
    markable.add_to_back(second)

    subs = markable.submobjects
    assert subs.index(second) < subs.index(first)


# remove() routing =====================================================================


def test_remove_vmobject_no_longer_in_submobjects(
    markable: ConcreteMarkable, plain_vmobject: mn.VMobject
) -> None:
    markable.add(plain_vmobject)
    markable.remove(plain_vmobject)

    assert plain_vmobject not in markable.submobjects


def test_remove_mark_no_longer_in_submobjects(
    markable: ConcreteMarkable, mark: Mark
) -> None:
    markable.add(mark)
    markable.remove(mark)

    assert mark not in markable.submobjects


def test_remove_child_markable_no_longer_in_submobjects(
    markable: ConcreteMarkable, child_markable: ConcreteMarkable
) -> None:
    markable.add(child_markable)
    markable.remove(child_markable)

    assert child_markable not in markable.submobjects


# 5. submobjects setter round-trip =====================================================


def test_submobjects_setter_routes_vmobject(
    markable: ConcreteMarkable, plain_vmobject: mn.VMobject
) -> None:
    markable.submobjects = [plain_vmobject]

    assert plain_vmobject in markable.submobjects


def test_submobjects_setter_routes_mark(markable: ConcreteMarkable, mark: Mark) -> None:
    markable.submobjects = [mark]

    assert mark in markable.submobjects


def test_submobjects_setter_routes_child_markable(
    markable: ConcreteMarkable, child_markable: ConcreteMarkable
) -> None:
    markable.submobjects = [child_markable]

    assert child_markable in markable.submobjects


def test_submobjects_setter_clears_previous_contents(
    markable: ConcreteMarkable,
    plain_vmobject: mn.VMobject,
    child_markable: ConcreteMarkable,
) -> None:
    markable.add(plain_vmobject)
    markable.submobjects = [child_markable]

    assert plain_vmobject not in markable.submobjects
    assert child_markable in markable.submobjects


def test_submobjects_setter_preserves_ordering(
    markable: ConcreteMarkable,
    plain_vmobject: mn.VMobject,
    mark: Mark,
    child_markable: ConcreteMarkable,
) -> None:
    markable.submobjects = [plain_vmobject, mark, child_markable]

    subs = markable.submobjects
    assert subs.index(plain_vmobject) < subs.index(mark) < subs.index(child_markable)


# rotate() with nested child Markable — no name-mangling regression ====================


def test_rotate_with_nested_child_markable_does_not_raise(
    markable: ConcreteMarkable, child_markable: ConcreteMarkable
) -> None:
    markable.add(child_markable)

    # Should not raise AttributeError due to name-mangling on _reposition_marks
    markable.rotate(mn.PI / 4)


def test_rotate_propagates_to_child_markable(markable: ConcreteMarkable) -> None:
    child = ConcreteMarkable()
    inner = mn.Square().shift(mn.RIGHT * 2)
    child.add(inner)
    markable.add(child)

    # Rotate about the origin so the off-centre square actually moves
    original_center = inner.get_center().copy()
    markable.rotate(mn.PI, about_point=mn.ORIGIN)

    assert not np.allclose(inner.get_center(), original_center)


# RotateMarkable animation is produced via the @mn.override_animation hook =============


def test_override_animation_produces_rotate_markable_instance(
    markable: ConcreteMarkable,
) -> None:
    # mn.Rotate(markable, ...) triggers the @mn.override_animation(mn.Rotate)
    # decorator defined on Markable, so the result must be a RotateMarkable.
    anim = mn.Rotate(markable, angle=mn.PI)

    assert isinstance(anim, _RotateMarkable)


def test_override_animation_is_not_bare_mn_rotate(
    markable: ConcreteMarkable,
) -> None:
    anim = mn.Rotate(markable, angle=mn.PI)

    # Confirm it is specifically the override subclass, not the plain base class
    assert type(anim) is _RotateMarkable


# RotateMarkable.interpolate_mobject reaches the correct final angle ===================


def test_rotate_markable_interpolate_at_1_reaches_target_angle(
    markable: ConcreteMarkable,
) -> None:
    angle = mn.PI / 3
    anim = _RotateMarkable(markable, angle=angle)
    anim.begin()

    anim.interpolate_mobject(1.0)

    assert np.isclose(anim.current_rotation, angle)


def test_rotate_markable_interpolate_partial_alpha(
    markable: ConcreteMarkable,
) -> None:
    angle = mn.PI
    alpha = 0.5
    anim = _RotateMarkable(markable, angle=angle)
    anim.begin()

    anim.interpolate_mobject(alpha)

    assert np.isclose(anim.current_rotation, angle * alpha)


def test_rotate_markable_initial_current_rotation_is_zero(
    markable: ConcreteMarkable,
) -> None:
    anim = _RotateMarkable(markable, angle=mn.PI)

    assert np.isclose(anim.current_rotation, 0.0)
