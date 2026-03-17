import os
from typing import Any

import manim as mn
import pytest

from manim_eng.components.base.component import Component

from .utils.dummy_component import DummyComponent, DummyComponentMockedPins


class _MockMathTex(mn.VMobject):
    """Stub MathTex that stores tex_strings without invoking LaTeX."""

    def __init__(self, *args: Any, font_size: float = 48, **_kwargs: Any) -> None:
        super().__init__()
        self.tex_strings: list[str] = list(args)
        self.font_size = font_size


@pytest.fixture(autouse=True)
def mock_mathtex(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mn, "MathTex", _MockMathTex)


# Create the media directory required by some of the tests if it doesn't already exist
# Ordinarily Manim would create this, but the tests run Manim code outside the usual
# framework (i.e. not within a Scene's construct() method), so we have to do some work
# ourselves.
os.makedirs("media", exist_ok=True)


@pytest.fixture
def dummy_component() -> Component:
    return DummyComponent()


@pytest.fixture
def dummy_component_mocked_pins() -> Component:
    return DummyComponentMockedPins()
