import copy

import numpy as np
import pytest
from manim_eng._utils import utils


@pytest.mark.parametrize(
    ("vector", "expected"),
    [
        pytest.param([1, 0, 0], [1, 0, 0], id="unit vector doesn't change"),
        pytest.param([1, 1, 0], [0.70710678, 0.70710678, 0], id="non-unit vector"),
    ],
)
def test_normalised(vector: list[float], expected: list[float]) -> None:
    vector = np.array(vector)  # type: ignore[assignment]
    vector_original = copy.deepcopy(vector)
    expected = np.array(expected)  # type: ignore[assignment]

    result = utils.normalised(vector)

    assert np.allclose(result, expected, rtol=0.001)
    assert np.all(vector == vector_original)


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
    vector = np.array(vector)  # type: ignore[assignment]
    vector_original = copy.deepcopy(vector)
    expected = np.array(expected)  # type: ignore[assignment]

    result = utils.cardinalised(vector, margin)

    assert np.allclose(result, expected, rtol=0.00001)
    assert np.all(vector == vector_original)
