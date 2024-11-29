from unittest import mock

import manim as mn
import manim.typing as mnt
import numpy as np
import pytest
from manim_eng import Node
from manim_eng.components.base import Terminal


@pytest.mark.parametrize(
    ("terminal_directions_and_visibilities", "expected"),
    [
        pytest.param([], [], id="no terminals returns empty list"),
        pytest.param(
            [(mn.UP, False), (mn.DOWN, False), (mn.LEFT, False)],
            [],
            id="no visible terminals returns empty list",
        ),
        pytest.param(
            [(mn.RIGHT, True), (mn.LEFT, False), (mn.DOWN, False), (mn.UP, True)],
            [0.0, 0.5 * np.pi],
            id="only returns visible terminals",
        ),
        pytest.param(
            [(mn.UP, True), (mn.DL, True), (mn.UR, True)],
            [-0.75 * np.pi, 0.25 * np.pi, 0.5 * np.pi],
            id="angle list is sorted",
        ),
    ],
)
def test_get_visible_terminal_angles(
    terminal_directions_and_visibilities: list[tuple[mnt.Vector3D, bool]],
    expected: list[float],
) -> None:
    node = Node()
    for direction, visibility in terminal_directions_and_visibilities:
        terminal_mock = mock.MagicMock(Terminal)
        terminal_mock.direction = direction
        terminal_mock.is_visible.return_value = visibility
        node.terminals.append(terminal_mock)

    actual = node._get_visible_terminal_angles()

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
