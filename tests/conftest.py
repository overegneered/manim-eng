import os
from typing import Any

import manim as mn
import pytest

from manim_eng import Wire
from manim_eng.circuits.node import Node
from manim_eng.components.base.component import Component
from manim_eng.components.base.pin import Pin

from .utils.dummy_component import DummyComponent, DummyComponentMockedPins


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
    start = Pin(mn.LEFT, mn.LEFT)
    end = Pin(mn.RIGHT, mn.RIGHT)
    return Wire(start, end)


@pytest.fixture
def node() -> Node:
    # mypy can't work this one out
    return Node().move_to(mn.ORIGIN)  # type: ignore[no-any-return]


@pytest.fixture
def wire_with_current() -> Wire:
    start = Pin(mn.LEFT, mn.LEFT)
    end = Pin(mn.RIGHT, mn.RIGHT)
    w = Wire(start, end)
    w.current.set(label="I")
    return w


@pytest.fixture
def dummy_component() -> Component:
    return DummyComponent()


@pytest.fixture
def dummy_component_mocked_pins() -> Component:
    return DummyComponentMockedPins()
