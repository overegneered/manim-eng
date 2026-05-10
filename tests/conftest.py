import os
import sys
from pathlib import Path
from typing import Any

import manim as mn
import pytest

from manim_eng import Wire
from manim_eng.circuits.node import Node
from manim_eng.components.base.component import Component

from .utils.dummy_component import (
    DummyComponent,
    DummyComponentMockedPins,
    DummyComponentOffCentre,
)
from .utils.pin_mocked import PinMockedParent

# Add the test root to the path to allow absolute addressing to the `utils` subdirectory
sys.path.insert(0, str(Path(__file__).parent))


class _MockMathTex(mn.VMobject):
    """Stub MathTex that stores tex_strings without invoking LaTeX."""

    def __init__(self, *args: Any, font_size: float = 48, **_kwargs: Any) -> None:
        super().__init__()
        self.tex_strings: list[str] = list(args)
        self.font_size = font_size


@pytest.fixture(autouse=True)
def _mock_mathtex(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mn, "MathTex", _MockMathTex)


# Create the media directory required by some of the tests if it doesn't already exist
# Ordinarily Manim would create this, but the tests run Manim code outside the usual
# framework (i.e. not within a Scene's construct() method), so we have to do some work
# ourselves.
os.makedirs("media", exist_ok=True)


@pytest.fixture
def wire() -> Wire:
    start = PinMockedParent(mn.LEFT, mn.LEFT)
    end = PinMockedParent(mn.RIGHT, mn.RIGHT)
    return Wire(start, end)


@pytest.fixture
def node() -> Node:
    # mypy can't work this one out
    return Node().move_to(mn.ORIGIN)  # type: ignore[no-any-return]


@pytest.fixture
def wire_with_current() -> Wire:
    start = PinMockedParent(mn.LEFT, mn.LEFT)
    end = PinMockedParent(mn.RIGHT, mn.RIGHT)
    w = Wire(start, end)
    w.current.set(label="I")
    return w


@pytest.fixture
def wire_with_one_corner() -> Wire:
    # Perpendicular pins: one pointing RIGHT from origin, one pointing UP from (1,1,0).
    # get_corner_points() for perpendicular pins returns exactly 1 corner point.
    start = PinMockedParent(mn.ORIGIN, mn.RIGHT)
    end = PinMockedParent(mn.RIGHT + mn.UP, mn.UP)
    return Wire(start, end)


@pytest.fixture
def wire_with_two_corners() -> Wire:
    # Parallel (same-direction) pins produce 2 corner points from get_corner_points().
    start = PinMockedParent(mn.LEFT * 2, mn.RIGHT)
    end = PinMockedParent(mn.RIGHT * 2 + mn.UP, mn.RIGHT)
    return Wire(start, end)


@pytest.fixture
def dummy_component() -> Component:
    return DummyComponent()


@pytest.fixture
def dummy_component_off_centre() -> Component:
    return DummyComponentOffCentre()


@pytest.fixture
def dummy_component_mocked_pins() -> Component:
    return DummyComponentMockedPins()
