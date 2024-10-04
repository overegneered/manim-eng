import copy

import numpy as np
import pytest
from manim_eng._utils import utils

STANDARD_MARGIN = np.deg2rad(5)


@pytest.mark.parametrize(
    ("vector", "margin", "expected"),
    [
        pytest.param([1, 1, 0], STANDARD_MARGIN, [1, 1, 0], id="no action necessary"),
        pytest.param(
            [9.99048222, 0.43619387, 0],
            STANDARD_MARGIN,
            [10, 0, 0],
            id="snapped vectors maintain magnitude",
        ),
        pytest.param(
            [0.9961947, 0.08715574, 0],
            STANDARD_MARGIN,
            [1, 0, 0],
            id="on positive margin (right)",
        ),
        pytest.param(
            [0.9961947, -0.08715574, 0],
            STANDARD_MARGIN,
            [1, 0, 0],
            id="on negative margin (right)",
        ),
        pytest.param(
            [-0.9961947, 0.08715574, 0],
            STANDARD_MARGIN,
            [-1, 0, 0],
            id="on negative margin (left)",
        ),
        pytest.param(
            [-0.9961947, -0.08715574, 0],
            STANDARD_MARGIN,
            [-1, 0, 0],
            id="on positive margin (left)",
        ),
        pytest.param(
            [0.08715574, 0.9961947, 0],
            STANDARD_MARGIN,
            [0, 1, 0],
            id="on negative margin (up)",
        ),
        pytest.param(
            [-0.08715574, 0.9961947, 0],
            STANDARD_MARGIN,
            [0, 1, 0],
            id="on positive margin (up)",
        ),
        pytest.param(
            [-0.08715574, -0.9961947, 0],
            STANDARD_MARGIN,
            [0, -1, 0],
            id="on negative margin (down)",
        ),
        pytest.param(
            [0.08715574, -0.9961947, 0],
            STANDARD_MARGIN,
            [0, -1, 0],
            id="on positive margin (down)",
        ),
    ],
)
def test_cardinalised(
    vector: list[float],
    margin: float,
    expected: list[float],
) -> None:
    vector_original = copy.deepcopy(vector)

    result = utils.cardinalised(vector, margin)

    assert np.allclose(result, expected)
    assert np.all(vector == vector_original)


@pytest.mark.parametrize(
    ("vector", "expected"),
    [
        pytest.param([1, 0, 0], [1, 0, 0], id="no action necessary"),
        pytest.param(
            [0.7071067811865475, 0.7071067811865475, 0],
            [1, 0, 0],
            id="45 degrees snaps to the vertical preferentially",
        ),
    ],
)
def test_cardinalised_no_margin_given(
    vector: list[float], expected: list[float]
) -> None:
    result = utils.cardinalised(vector)

    assert np.allclose(result, expected)
