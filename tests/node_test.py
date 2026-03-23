from unittest import mock

import manim as mn
import manim.typing as mnt
import numpy as np
import pytest

from manim_eng import Node
from manim_eng.components.base.component import Component
from manim_eng.components.base.pin import Pin


@pytest.mark.parametrize(
    ("pin_directions_and_visibilities", "expected"),
    [
        pytest.param([], [], id="no pins returns empty list"),
        pytest.param(
            [(mn.UP, False), (mn.DOWN, False), (mn.LEFT, False)],
            [],
            id="no visible pins returns empty list",
        ),
        pytest.param(
            [(mn.RIGHT, True), (mn.LEFT, False), (mn.DOWN, False), (mn.UP, True)],
            [0.0, 0.5 * np.pi],
            id="only returns visible pins",
        ),
        pytest.param(
            [(mn.UP, True), (mn.DL, True), (mn.UR, True)],
            [-0.75 * np.pi, 0.25 * np.pi, 0.5 * np.pi],
            id="angle list is sorted",
        ),
    ],
)
def test_get_visible_pin_angles(
    pin_directions_and_visibilities: list[tuple[mnt.Vector3D, bool]],
    expected: list[float],
) -> None:
    node = Node()
    for direction, visibility in pin_directions_and_visibilities:
        pin_mock = mock.MagicMock(Pin)
        pin_mock.direction = direction
        pin_mock.is_visible.return_value = visibility
        node.pins.append(pin_mock)

    actual = node._get_visible_pin_angles()

    assert np.allclose(actual, expected)


@pytest.mark.parametrize(
    ("angles", "expected"),
    [
        pytest.param([], [], id="no angles returns empty list"),
        pytest.param([30], [-150], id="single angle returns opposite angle"),
        pytest.param([0, 80], [-140], id="two angles in list"),
        pytest.param([0, 180], [-90, 90], id="two input angles with two best options"),
        pytest.param(
            [-90, -45, 0], [135], id="three input angles with one best option"
        ),
        pytest.param(
            [-90, 0, 135], [-157.5, 67.5], id="three input angles with two best options"
        ),
        pytest.param(
            [-120, 0, 120],
            [-60, 60, 180],
            id="three input angles with three best options",
        ),
        pytest.param(
            [-120, -90, 0, 135], [67.5], id="four input angles with one best option"
        ),
    ],
)
def test_midangles_of_largest_gaps_between_list_of_angles(
    angles: list[float], expected: list[float]
) -> None:
    angles = [angle * mn.DEGREES for angle in angles]
    expected = [angle * mn.DEGREES for angle in expected]

    actual = Node._midangles_of_largest_gaps_between_list_of_angles(angles)

    assert np.allclose(actual, expected)


def test_next_to_with_pin_uses_pin_tip_as_reference() -> None:
    """Passing a Pin moves the node relative to the pin's tip."""
    node = Node().move_to(mn.ORIGIN)
    pin = Pin(position=mn.RIGHT * 3, direction=mn.RIGHT)

    node.next_to(pin)

    # The node should be to the right of the pin tip (i.e. further right than tip).
    assert node.get_center()[0] > pin.tip[0]


def test_next_to_with_pin_uses_pin_direction_by_default() -> None:
    """When a Pin is passed without an explicit direction, pin.direction is used."""
    node = Node().move_to(mn.ORIGIN)
    pin = Pin(position=mn.ORIGIN, direction=mn.UP)

    node.next_to(pin)

    # Pin points UP, so the node should end up above the pin tip.
    assert node.get_center()[1] > pin.tip[1]


def test_next_to_with_pin_explicit_direction_overrides_pin_direction() -> None:
    """An explicit direction argument overrides the pin's own direction."""
    # Place the pin pointing UP so its direction and the override (RIGHT) are distinct.
    pin = Pin(position=mn.ORIGIN, direction=mn.UP)

    # Place the node using the pin's direction (UP) — baseline.
    node_default = Node().move_to(mn.ORIGIN)
    node_default.next_to(pin)  # uses pin.direction == UP

    # Place another node using an explicit RIGHT direction override.
    node_override = Node().move_to(mn.ORIGIN)
    node_override.next_to(pin, direction=mn.RIGHT)

    # The two placements must differ: one is above the tip, the other is to its right.
    # "Above" means larger y; "right" means larger x relative to the tip.
    assert node_default.get_center()[1] > node_override.get_center()[1]
    assert node_override.get_center()[0] > node_default.get_center()[0]


def test_next_to_with_mobject_defaults_to_right() -> None:
    """Passing a plain Mobject without direction places the node to the right."""
    node = Node().move_to(mn.ORIGIN)
    ref = mn.Dot().move_to(mn.ORIGIN)

    node.next_to(ref)

    assert node.get_center()[0] > ref.get_center()[0]


def test_next_to_with_point_and_explicit_direction() -> None:
    """Passing a point with an explicit direction places the node correctly."""
    node = Node().move_to(mn.ORIGIN)

    node.next_to(mn.ORIGIN, direction=mn.LEFT)

    assert node.get_center()[0] < 0


def test_next_to_returns_self() -> None:
    """next_to returns the node itself for method chaining."""
    node = Node().move_to(mn.ORIGIN)
    result = node.next_to(mn.ORIGIN)

    assert result is node


def test_next_to_only_on_node_not_component() -> None:
    """next_to is defined on Node but not on the Component base class."""
    assert "next_to" not in Component.__dict__
    assert "next_to" in Node.__dict__


def test_next_to_forwards_optional_kwargs() -> None:
    """Optional kwargs such as buff are forwarded to Mobject.next_to."""
    ref = mn.Dot().move_to(mn.ORIGIN)

    node_default = Node().move_to(mn.ORIGIN)
    node_default.next_to(ref)

    node_large_buff = Node().move_to(mn.ORIGIN)
    node_large_buff.next_to(ref, buff=5.0)

    default_distance = np.linalg.norm(node_default.get_center() - ref.get_center())
    large_buff_distance = np.linalg.norm(
        node_large_buff.get_center() - ref.get_center()
    )

    assert large_buff_distance > default_distance


def test_next_to_with_point_defaults_to_right() -> None:
    """Passing a plain point without direction uses mn.RIGHT as the default."""
    node = Node().move_to(mn.ORIGIN)

    node.next_to(np.array([0.0, 0.0, 0.0]))

    assert node.get_center()[0] > 0


@pytest.mark.parametrize(
    ("angles", "expected"),
    [
        pytest.param([], mn.UP, id="no angles defaults to upwards"),
        pytest.param([-90], mn.DOWN, id="one angle will always select that angle"),
        pytest.param(
            [-45, 30, 45],
            mn.normalize(mn.UR),
            id="angle associated with greater y-coordinate will be chosen",
        ),
    ],
)
def test_topmost_angle_as_direction(
    angles: list[float], expected: mnt.Vector3D
) -> None:
    angles = [angle * mn.DEGREES for angle in angles]
    actual = Node._topmost_angle_as_direction(angles)

    assert np.allclose(actual, expected)
