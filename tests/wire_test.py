from collections.abc import Callable

import manim as mn
import numpy as np
import pytest

from manim_eng import ManualWire, Wire
from manim_eng.circuits.node import Node
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


# split_at — structural / return-value =================================================


def _make_horizontal_wire() -> Wire:
    """Return a simple left-to-right wire for use in split_at tests."""
    start = Pin(mn.LEFT * 2, mn.RIGHT)
    end = Pin(mn.RIGHT * 2, mn.LEFT)
    return Wire(start, end)


def test_split_at_returns_tuple_of_wire_node_wire() -> None:
    wire = _make_horizontal_wire()

    result = wire.split_at(0.5)

    assert isinstance(result, tuple)
    assert len(result) == 3  # noqa: PLR2004
    start_portion, node, end_portion = result
    assert isinstance(start_portion, Wire)
    assert isinstance(node, Node)
    assert isinstance(end_portion, Wire)


def test_split_at_start_wire_retains_original_start_pin() -> None:
    start_pin = Pin(mn.LEFT * 2, mn.RIGHT)
    end_pin = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start_pin, end_pin)

    start_portion, _node, _end_portion = wire.split_at(0.5)

    assert start_portion._start is start_pin


def test_split_at_end_wire_retains_original_end_pin() -> None:
    start_pin = Pin(mn.LEFT * 2, mn.RIGHT)
    end_pin = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start_pin, end_pin)

    _start_portion, _node, end_portion = wire.split_at(0.5)

    assert end_portion._end is end_pin


def test_split_at_node_is_placed_at_correct_position() -> None:
    wire = _make_horizontal_wire()
    alpha = 0.5
    expected_point = wire.point_from_proportion(alpha)

    _start_portion, node, _end_portion = wire.split_at(alpha)

    assert np.allclose(node.get_center(), expected_point, atol=1e-4)


def test_split_at_node_pins_face_towards_start_and_end_wire() -> None:
    # On a straight left-to-right wire, the node pin towards the start should
    # point LEFT and the one towards the end should point RIGHT (antiparallel).
    start_pin = Pin(mn.LEFT * 2, mn.RIGHT)
    end_pin = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start_pin, end_pin)

    start_portion, _node, end_portion = wire.split_at(0.5)

    # The start portion ends at a node pin; that pin's direction should point
    # back towards the start (LEFT from node's perspective).
    node_start_pin = start_portion._end
    node_end_pin = end_portion._start

    # Check for anti-parallelism
    dot = np.dot(
        mn.normalize(node_start_pin.direction),
        mn.normalize(node_end_pin.direction),
    )
    assert np.isclose(dot, -1.0, atol=1e-4)


def test_split_at_start_portion_end_pin_belongs_to_node() -> None:
    wire = _make_horizontal_wire()

    start_portion, node, _end_portion = wire.split_at(0.5)

    assert start_portion._end in node.pins


def test_split_at_end_portion_start_pin_belongs_to_node() -> None:
    wire = _make_horizontal_wire()

    _start_portion, node, end_portion = wire.split_at(0.5)

    assert end_portion._start in node.pins


# split_at — pin attachment state ======================================================


def test_split_at_detaches_original_wire_from_start_pin() -> None:
    start_pin = Pin(mn.LEFT * 2, mn.RIGHT)
    end_pin = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start_pin, end_pin)

    wire.split_at(0.5)

    assert start_pin.attached_wire is not wire


def test_split_at_detaches_original_wire_from_end_pin() -> None:
    start_pin = Pin(mn.LEFT * 2, mn.RIGHT)
    end_pin = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start_pin, end_pin)

    wire.split_at(0.5)

    assert end_pin.attached_wire is not wire


def test_split_at_start_pin_is_attached_to_start_portion() -> None:
    start_pin = Pin(mn.LEFT * 2, mn.RIGHT)
    end_pin = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start_pin, end_pin)

    start_portion, _node, _end_portion = wire.split_at(0.5)

    assert start_pin.attached_wire is start_portion


def test_split_at_end_pin_is_attached_to_end_portion() -> None:
    start_pin = Pin(mn.LEFT * 2, mn.RIGHT)
    end_pin = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start_pin, end_pin)

    _start_portion, _node, end_portion = wire.split_at(0.5)

    assert end_pin.attached_wire is end_portion


# split_at — alpha boundary / error ====================================================


def test_split_at_raises_value_error_if_alpha_less_than_zero() -> None:
    wire = _make_horizontal_wire()

    with pytest.raises(ValueError, match=r"`alpha` must be strictly between"):
        wire.split_at(-0.1)


def test_split_at_raises_value_error_if_alpha_greater_than_one() -> None:
    wire = _make_horizontal_wire()

    with pytest.raises(ValueError, match=r"`alpha` must be strictly between"):
        wire.split_at(1.1)


def test_split_at_raises_value_error_if_alpha_exactly_zero() -> None:
    # alpha=0.0 causes point_from_proportion(0.0 - epsilon) which may crash or
    # return a position outside the wire's path.
    wire = _make_horizontal_wire()

    with pytest.raises(ValueError, match=r"`alpha` must be strictly between"):
        wire.split_at(0.0)


def test_split_at_raises_value_error_if_alpha_exactly_one() -> None:
    # alpha=1.0 causes point_from_proportion(1.0 + epsilon) which may crash or
    # return a position outside the wire's path.
    wire = _make_horizontal_wire()

    with pytest.raises(ValueError, match=r"`alpha` must be strictly between"):
        wire.split_at(1.0)


# split_at — current placement =========================================================


def test_split_at_places_current_on_start_portion_when_it_falls_before_split() -> None:
    # Current is at alpha=0.3, split is at alpha=0.5 — current falls on start half.
    start = Pin(mn.LEFT * 2, mn.RIGHT)
    end = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start, end)
    wire.current.set(label="I", alpha=0.3)

    start_portion, _node, end_portion = wire.split_at(0.5)

    assert start_portion.current._triangle in start_portion.current.submobjects
    assert end_portion.current._triangle not in end_portion.current.submobjects


def test_split_at_places_current_on_end_portion_when_it_falls_after_split() -> None:
    # Current is at alpha=0.7, split is at alpha=0.5 — current falls on end half.
    start = Pin(mn.LEFT * 2, mn.RIGHT)
    end = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start, end)
    wire.current.set(label="I", alpha=0.7)

    start_portion, _node, end_portion = wire.split_at(0.5)

    assert end_portion.current._triangle in end_portion.current.submobjects
    assert start_portion.current._triangle not in start_portion.current.submobjects


def test_split_at_remaps_current_alpha_correctly_for_start_portion() -> None:
    # Current at alpha=0.25, split at alpha=0.5 → remapped alpha = 0.25/0.5 = 0.5.
    start = Pin(mn.LEFT * 2, mn.RIGHT)
    end = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start, end)
    wire.current.set(label="I", alpha=0.25)

    start_portion, _node, _end_portion = wire.split_at(0.5)

    assert np.isclose(start_portion.current._alpha, 0.5)


def test_split_at_remaps_current_alpha_correctly_for_end_portion() -> None:
    # Current at alpha=0.75, split at alpha=0.5 → remapped alpha = (0.75-0.5)/0.5 = 0.5.
    start = Pin(mn.LEFT * 2, mn.RIGHT)
    end = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start, end)
    wire.current.set(label="I", alpha=0.75)

    _start_portion, _node, end_portion = wire.split_at(0.5)

    assert np.isclose(end_portion.current._alpha, 0.5)


def test_split_at_with_no_current_does_not_error() -> None:
    # A wire with no current set should not raise.
    wire = _make_horizontal_wire()

    wire.split_at(0.5)


# split_at — geometry ==================================================================


def test_split_at_alpha_quarter_places_node_at_one_quarter_point() -> None:
    # Wire goes from x=-2 to x=+2 (length 4), so the 25% point is at x=-1.
    start_pin = Pin(mn.LEFT * 2, mn.RIGHT)
    end_pin = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start_pin, end_pin)
    alpha = 0.25
    expected = wire.point_from_proportion(alpha)

    _start_portion, node, _end_portion = wire.split_at(alpha)

    assert np.allclose(node.get_center(), expected, atol=1e-4)


# split_at — inverted current placement ===============================================


def _make_wire_with_inverted_current(alpha: float) -> Wire:
    """Return a horizontal wire with an inverted current arrow at the given alpha."""
    start = Pin(mn.LEFT * 2, mn.RIGHT)
    end = Pin(mn.RIGHT * 2, mn.LEFT)
    wire = Wire(start, end)
    wire.current.set(label="I", alpha=alpha, invert=True)
    return wire


def test_split_at_inverted_current_before_split_placed_on_start_portion() -> None:
    # alpha=0.3, invert=True → geometric position from start = 1 - 0.3 = 0.7.
    # Split at 0.8 → 0.7 < 0.8, so arrow falls on start portion.
    wire = _make_wire_with_inverted_current(alpha=0.3)

    start_portion, _node, end_portion = wire.split_at(0.8)

    assert start_portion.current._triangle in start_portion.current.submobjects
    assert end_portion.current._triangle not in end_portion.current.submobjects


def test_split_at_inverted_current_after_split_placed_on_end_portion() -> None:
    # alpha=0.3, invert=True → geometric position from start = 1 - 0.3 = 0.7.
    # Split at 0.5 → 0.7 >= 0.5, so arrow falls on end portion.
    wire = _make_wire_with_inverted_current(alpha=0.3)

    start_portion, _node, end_portion = wire.split_at(0.5)

    assert end_portion.current._triangle in end_portion.current.submobjects
    assert start_portion.current._triangle not in start_portion.current.submobjects


def test_split_at_inverted_current_alpha_remapped_correctly_for_start_portion() -> None:
    # alpha=0.2, invert=True → geometric position = 1 - 0.2 = 0.8. Split at 0.9.
    # 0.8 < 0.9 → start portion.
    # Remapped geometric alpha within start: 0.8 / 0.9.
    # Since invert=True, new _alpha = 1 - (0.8 / 0.9).
    wire = _make_wire_with_inverted_current(alpha=0.2)

    start_portion, _node, _end_portion = wire.split_at(0.9)

    assert np.isclose(start_portion.current._alpha, 1 - (0.8 / 0.9))


def test_split_at_inverted_current_alpha_remapped_correctly_for_end_portion() -> None:
    # alpha=0.4, invert=True → geometric position = 1 - 0.4 = 0.6. Split at 0.5.
    # 0.6 >= 0.5 → end portion.
    # Remapped geometric alpha within end: (0.6 - 0.5) / (1 - 0.5) = 0.2.
    # Since invert=True, new _alpha = 1 - 0.2 = 0.8.
    wire = _make_wire_with_inverted_current(alpha=0.4)

    _start_portion, _node, end_portion = wire.split_at(0.5)

    assert np.isclose(end_portion.current._alpha, 0.8)


# split_at — container parameter =======================================================


def test_split_at_with_mobject_container_removes_wire_from_container() -> None:
    wire = _make_horizontal_wire()
    container = mn.VGroup(wire)

    wire.split_at(0.5, container=container)

    assert wire not in container.submobjects


def test_split_at_with_mobject_container_adds_portions_and_node() -> None:
    wire = _make_horizontal_wire()
    container = mn.VGroup(wire)

    start_portion, node, end_portion = wire.split_at(0.5, container=container)

    assert start_portion in container.submobjects
    assert node in container.submobjects
    assert end_portion in container.submobjects


def test_split_at_with_no_container_does_not_modify_any_group() -> None:
    wire = _make_horizontal_wire()
    container = mn.VGroup(wire)

    wire.split_at(0.5)

    assert wire in container.submobjects


def test_split_at_with_container_still_returns_tuple() -> None:
    wire = _make_horizontal_wire()
    container = mn.VGroup(wire)

    result = wire.split_at(0.5, container=container)

    assert isinstance(result, tuple)
    assert len(result) == 3  # noqa: PLR2004
    start_portion, node, end_portion = result
    assert isinstance(start_portion, Wire)
    assert isinstance(node, Node)
    assert isinstance(end_portion, Wire)


# split_at_corners ====================================================================


def test_split_at_corners_no_corners_returns_self_and_empty_nodes(wire: Wire) -> None:
    # Wire.get_corner_points() always returns 1 or 2 points for any valid pin pair,
    # so we monkeypatch it to return [] to exercise the early-exit branch.
    wire.get_corner_points = list  # type: ignore[method-assign]

    segments, nodes = wire.split_at_corners()

    assert segments == [wire]
    assert nodes == []


def test_split_at_corners_one_corner_returns_two_segments_one_node(
    wire_with_one_corner: Wire,
) -> None:
    segments, nodes = wire_with_one_corner.split_at_corners()

    assert len(segments) == 2  # noqa: PLR2004
    assert len(nodes) == 1


def test_split_at_corners_two_corners_returns_three_segments_two_nodes(
    wire_with_two_corners: Wire,
) -> None:
    segments, nodes = wire_with_two_corners.split_at_corners()

    assert len(segments) == 3  # noqa: PLR2004
    assert len(nodes) == 2  # noqa: PLR2004


def test_split_at_corners_segments_retain_original_start_and_end_pins(
    wire_with_one_corner: Wire,
) -> None:
    original_start = wire_with_one_corner._start
    original_end = wire_with_one_corner._end

    segments, _nodes = wire_with_one_corner.split_at_corners()

    assert segments[0]._start is original_start
    assert segments[-1]._end is original_end


def test_split_at_corners_nodes_are_at_corner_positions(
    wire_with_one_corner: Wire,
) -> None:
    corner_points = wire_with_one_corner.get_corner_points()

    _segments, nodes = wire_with_one_corner.split_at_corners()

    for node, corner in zip(nodes, corner_points, strict=True):
        assert np.allclose(node.get_center(), corner, atol=1e-4)


def test_split_at_corners_with_container_removes_wire_and_adds_results(
    wire_with_one_corner: Wire,
) -> None:
    container = mn.VGroup(wire_with_one_corner)

    segments, nodes = wire_with_one_corner.split_at_corners(container=container)

    assert wire_with_one_corner not in container.submobjects
    for seg in segments:
        assert seg in container.submobjects
    for node in nodes:
        assert node in container.submobjects


def test_split_at_corners_with_no_container_does_not_modify_group(
    wire_with_one_corner: Wire,
) -> None:
    container = mn.VGroup(wire_with_one_corner)

    wire_with_one_corner.split_at_corners()

    assert wire_with_one_corner in container.submobjects


def test_split_at_corners_with_current_places_it_on_correct_segment(
    wire_with_one_corner: Wire,
) -> None:
    # Place current arrow at alpha=0.1 — well into the first segment.
    wire_with_one_corner.current.set(label="I", alpha=0.1)

    segments, _nodes = wire_with_one_corner.split_at_corners()

    # The triangle must appear in exactly one segment's current submobjects.
    triangle_in = [
        seg for seg in segments if seg.current._triangle in seg.current.submobjects
    ]
    triangle_absent = [
        seg for seg in segments if seg.current._triangle not in seg.current.submobjects
    ]
    assert len(triangle_in) == 1
    assert len(triangle_absent) == 1
    # alpha=0.1 is early in the wire, so it should be on the first segment.
    assert triangle_in[0] is segments[0]


# split_at_corner ======================================================================

# structural / return-value ------------------------------------------------------------


def test_split_at_corner_returns_tuple_of_wire_node_wire(
    wire_with_one_corner: Wire,
) -> None:
    result = wire_with_one_corner.split_at_corner(0)

    assert isinstance(result, tuple)
    assert len(result) == 3  # noqa: PLR2004
    start_portion, node, end_portion = result
    assert isinstance(start_portion, Wire)
    assert isinstance(node, Node)
    assert isinstance(end_portion, Wire)


def test_split_at_corner_start_portion_retains_original_start_pin(
    wire_with_one_corner: Wire,
) -> None:
    original_start = wire_with_one_corner._start

    start_portion, _node, _end_portion = wire_with_one_corner.split_at_corner(0)

    assert start_portion._start is original_start


def test_split_at_corner_end_portion_retains_original_end_pin(
    wire_with_one_corner: Wire,
) -> None:
    original_end = wire_with_one_corner._end

    _start_portion, _node, end_portion = wire_with_one_corner.split_at_corner(0)

    assert end_portion._end is original_end


# node position ------------------------------------------------------------------------


def test_split_at_corner_node_placed_at_corner_position(
    wire_with_one_corner: Wire,
) -> None:
    corner_points = wire_with_one_corner.get_corner_points()

    _start_portion, node, _end_portion = wire_with_one_corner.split_at_corner(0)

    assert np.allclose(node.get_center(), corner_points[0], atol=1e-4)


def test_split_at_corner_index_zero_on_two_corner_wire_splits_at_first_corner(
    wire_with_two_corners: Wire,
) -> None:
    corner_points = wire_with_two_corners.get_corner_points()

    _start_portion, node, _end_portion = wire_with_two_corners.split_at_corner(0)

    assert np.allclose(node.get_center(), corner_points[0], atol=1e-4)


def test_split_at_corner_index_one_on_two_corner_wire_splits_at_second_corner(
    wire_with_two_corners: Wire,
) -> None:
    corner_points = wire_with_two_corners.get_corner_points()

    _start_portion, node, _end_portion = wire_with_two_corners.split_at_corner(1)

    assert np.allclose(node.get_center(), corner_points[1], atol=1e-4)


# negative indexing --------------------------------------------------------------------


def test_split_at_corner_negative_index_minus_one_is_last_corner(
    wire_with_one_corner: Wire,
) -> None:
    corner_points = wire_with_one_corner.get_corner_points()

    _start_portion, node, _end_portion = wire_with_one_corner.split_at_corner(-1)

    assert np.allclose(node.get_center(), corner_points[0], atol=1e-4)


def test_split_at_corner_negative_index_minus_one_on_two_corner_wire(
    wire_with_two_corners: Wire,
) -> None:
    corner_points = wire_with_two_corners.get_corner_points()

    _start_portion, node, _end_portion = wire_with_two_corners.split_at_corner(-1)

    assert np.allclose(node.get_center(), corner_points[1], atol=1e-4)


def test_split_at_corner_negative_index_minus_two_on_two_corner_wire(
    wire_with_two_corners: Wire,
) -> None:
    corner_points = wire_with_two_corners.get_corner_points()

    _start_portion, node, _end_portion = wire_with_two_corners.split_at_corner(-2)

    assert np.allclose(node.get_center(), corner_points[0], atol=1e-4)


# error cases --------------------------------------------------------------------------


def test_split_at_corner_raises_value_error_if_no_corners(
    wire_with_one_corner: Wire,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(wire_with_one_corner, "get_corner_points", list, raising=False)

    with pytest.raises(ValueError, match="no corners"):
        wire_with_one_corner.split_at_corner(0)


def test_split_at_corner_raises_index_error_if_index_too_large(
    wire_with_one_corner: Wire,
) -> None:
    with pytest.raises(IndexError):
        wire_with_one_corner.split_at_corner(1)


def test_split_at_corner_raises_index_error_if_index_too_negative(
    wire_with_one_corner: Wire,
) -> None:
    with pytest.raises(IndexError):
        wire_with_one_corner.split_at_corner(-2)


def test_split_at_corner_raises_index_error_for_large_positive_index_on_two_corner_wire(
    wire_with_two_corners: Wire,
) -> None:
    with pytest.raises(IndexError):
        wire_with_two_corners.split_at_corner(2)


# container parameter ------------------------------------------------------------------


def test_split_at_corner_with_container_removes_wire_and_adds_results(
    wire_with_one_corner: Wire,
) -> None:
    container = mn.VGroup(wire_with_one_corner)

    start_portion, node, end_portion = wire_with_one_corner.split_at_corner(
        0, container=container
    )

    assert wire_with_one_corner not in container.submobjects
    assert start_portion in container.submobjects
    assert node in container.submobjects
    assert end_portion in container.submobjects


def test_split_at_corner_with_no_container_does_not_modify_group(
    wire_with_one_corner: Wire,
) -> None:
    container = mn.VGroup(wire_with_one_corner)

    wire_with_one_corner.split_at_corner(0)

    assert wire_with_one_corner in container.submobjects


def test_split_at_corner_with_container_still_returns_tuple(
    wire_with_one_corner: Wire,
) -> None:
    container = mn.VGroup(wire_with_one_corner)

    result = wire_with_one_corner.split_at_corner(0, container=container)

    assert isinstance(result, tuple)
    assert len(result) == 3  # noqa: PLR2004
    start_portion, node, end_portion = result
    assert isinstance(start_portion, Wire)
    assert isinstance(node, Node)
    assert isinstance(end_portion, Wire)
